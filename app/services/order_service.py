import logging
from fastapi import HTTPException
from sqlalchemy.orm import Session, selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from app.models.order import OrderModel
from app.models.order_item import OrderItemModel
from schemas.orders import Order, OrderUpdate, OrderCreate, OrderItem
from app.schemas.products import Product, ProductUpdate
from app.services.product_service import ProductService
from app.services.base_service import BaseService
from typing import List

logger = logging.getLogger(__name__)


class OrderService(BaseService):
    def __init__(self, db: AsyncSession):
        super().__init__(db)
        self.product_service = ProductService(db)

    async def get(self, skip: int = 0, limit: int = 10):
        """Retrieve a paginated list of orders with their items."""
        cache_key = self.get_cache_key(is_list=True, skip=skip, limit=limit)
        cached_orders = await self.redis_service.get_json(cache_key)
        if cached_orders:
            logger.info(f"Cache hit for orders: skip={skip}, limit={limit}")
            return cached_orders

        # Query paginated orders and load items
        query = (
            select(OrderModel)
            .offset(skip)
            .limit(limit)
            .options(selectinload(OrderModel.items))
        )
        db_order = await self.db.execute(query)
        orders = db_order.scalars().all()

        # Serialize and cache the result
        serialized_orders = [await self._serialize_order(order) for order in orders]
        await self.redis_service.set_json(
            cache_key, serialized_orders, expire=3600
        )  # Cache for 1 hour
        return orders

    async def get_one(self, id: int, use_cache=True):
        """Retrieve a single order by ID with its items."""
        cache_key = self.get_cache_key(id=id)
        if use_cache:
            cached_order = await self.redis_service.get_json(cache_key)
            if cached_order:
                logger.info(f"Cache hit for order id={id}")
                return cached_order

        # Query the order and load items
        query = (
            select(OrderModel)
            .where(OrderModel.id == id)
            .options(selectinload(OrderModel.items))
        )
        db_order = await self.db.execute(query)
        order = db_order.scalar()
        if not order:
            raise HTTPException(
                status_code=404, detail=f"Order with ID {id} not found."
            )

        # Serialize and cache the result
        serialized_order = await self._serialize_order(order)
        await self.redis_service.set_json(cache_key, serialized_order, expire=3600)
        return order

    async def create(self, obj: OrderCreate):
        """Create a new order with items."""
        logger.info(f"Creating order for user_id={obj.user_id} with items={obj.items}")
        db_order = OrderModel(user_id=obj.user_id)

        # Process items and save the order
        async with self.db.begin():
            await self._process_order_items(db_order, obj.items)
            self.db.add(db_order)
            await self.db.commit()
            await self.db.refresh(db_order)

        # Cache the created order
        await self._cache_order(db_order)

        # Invalidate the order list cache
        await self.invalidate_list_cache()

        return await self._serialize_order(db_order)

    async def _cache_order(self, db_order: OrderModel):
        """Cache the created or updated order."""
        cache_key = self.get_cache_key(id=db_order.id)
        serialized_order = await self._serialize_order(db_order)
        await self.redis_service.set_json(cache_key, serialized_order)

    async def update(self, id: int, obj: OrderUpdate):
        """Update an existing order and its items."""
        logger.info(f"Updating order id={id} with items={obj.items}")
        db_order = await self.get_one(id, use_cache=False)
        db_order_items = {item.product_id: item for item in db_order.items}

        # Handle updates or additions
        for updated_item in obj.items:
            if updated_item.product_id in db_order_items:
                await self._update_existing_item(
                    db_order_items[updated_item.product_id], updated_item
                )
            else:
                await self._add_new_item(db_order, updated_item)

        # Remove items not in the update
        updated_product_ids = {item.product_id for item in obj.items}
        await self._remove_items_not_in_update(db_order, updated_product_ids)

        self.db.add(db_order)
        await self.db.commit()

        # Cache the updated order
        await self._cache_order(db_order)

        # Invalidate the order list cache
        await self.invalidate_list_cache()

        return await self._serialize_order(db_order)

    async def delete(self, id: int):
        """Delete an order and restore stock for its items."""
        logger.info(f"Deleting order id={id}")
        db_order = await self.get_one(id, use_cache=False)
        for item in db_order.items:
            await self._adjust_product_stock(
                item.product_id, quantity_diff=item.quantity
            )
        await self.db.delete(db_order)
        await self.db.commit()

        # Invalidate the order list cache
        await self.invalidate_list_cache()

        return db_order

    async def _process_order_items(self, db_order: OrderModel, items: List[dict]):
        """Validate and process order items, including stock updates."""
        for item in items:
            product = await self._fetch_and_validate_product(
                item.product_id, item.quantity
            )
            product.quantity -= item.quantity
            await self.product_service.update(
                product.id, ProductUpdate(**product.model_dump())
            )
            db_order.items.append(
                OrderItemModel(
                    product_id=item.product_id,
                    quantity=item.quantity,
                    price_at_order_time=product.price,
                )
            )

    async def _update_existing_item(
        self, existing_item: OrderItemModel, updated_item: OrderItem
    ):
        """Update an existing order item."""
        quantity_diff = existing_item.quantity - updated_item.quantity
        await self._adjust_product_stock(
            existing_item.product_id, quantity_diff=quantity_diff
        )

        # Modify and track the item
        existing_item.quantity = updated_item.quantity
        self.db.add(existing_item)  # Explicitly track changes in the session

    async def _add_new_item(self, db_order: OrderModel, new_item: OrderItem):
        """Add a new order item to the order."""
        product = await self._fetch_and_validate_product(
            new_item.product_id, new_item.quantity
        )
        db_order.items.append(
            OrderItemModel(
                product_id=new_item.product_id,
                quantity=new_item.quantity,
                price_at_order_time=product.price,
            )
        )

    async def _remove_items_not_in_update(
        self, db_order: OrderModel, updated_product_ids: set[int]
    ):
        """Remove items no longer part of the updated order."""
        for item in db_order.items[:]:
            if item.product_id not in updated_product_ids:
                await self._adjust_product_stock(
                    item.product_id, quantity_diff=item.quantity
                )
                await self.db.delete(item)

    async def _adjust_product_stock(self, product_id: int, quantity_diff: int):
        """Adjust product stock by a given quantity difference."""
        if quantity_diff == 0:
            return
        product = await self.product_service.get_one(product_id, use_cache=False)
        product = Product.model_validate(product)
        if product.quantity + quantity_diff < 0:
            raise HTTPException(
                status_code=400,
                detail=f"Insufficient stock for product {product.name} (ID: {product.id})",
            )
        product.quantity += quantity_diff
        await self.product_service.update(
            product_id, ProductUpdate(**product.model_dump())
        )

    async def _serialize_order(self, db_order: OrderModel) -> dict:
        """Convert an order and its items to a dictionary."""
        return {
            "id": db_order.id,
            "user_id": db_order.user_id,
            "items": [
                {
                    "id": item.id,
                    "product_id": item.product_id,
                    "quantity": item.quantity,
                    "price_at_order_time": item.price_at_order_time,
                }
                for item in db_order.items
            ],
        }
