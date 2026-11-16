from flask import abort

from app import db
from app.models import Cart, CartItem, ProductVariant


class CartService:
    @staticmethod
    def get_or_create(user_id: int) -> Cart:
        cart = Cart.query.filter_by(user_id=user_id).first()
        if cart:
            return cart
        cart = Cart(user_id=user_id)
        db.session.add(cart)
        db.session.commit()
        return cart

    @staticmethod
    def add_item(user_id: int, variant_id: int, quantity: int = 1) -> Cart:
        if quantity < 1:
            abort(400, description="quantity must be >= 1")
        variant = ProductVariant.query.get_or_404(variant_id)
        if variant.stock < quantity:
            abort(400, description="insufficient_stock")
        cart = CartService.get_or_create(user_id)
        item = CartItem.query.filter_by(cart_id=cart.id, variant_id=variant_id).first()
        if item:
            new_qty = item.quantity + quantity
            if variant.stock < new_qty:
                abort(400, description="insufficient_stock")
            item.quantity = new_qty
        else:
            item = CartItem(cart_id=cart.id, variant_id=variant_id, quantity=quantity)
            db.session.add(item)
        db.session.commit()
        return cart

    @staticmethod
    def update_item(user_id: int, item_id: int, quantity: int) -> Cart:
        cart = CartService.get_or_create(user_id)
        item = CartItem.query.filter_by(id=item_id, cart_id=cart.id).first_or_404()
        if quantity < 1:
            db.session.delete(item)
        else:
            if item.variant.stock < quantity:
                abort(400, description="insufficient_stock")
            item.quantity = quantity
        db.session.commit()
        return cart

    @staticmethod
    def remove_item(user_id: int, item_id: int) -> Cart:
        cart = CartService.get_or_create(user_id)
        item = CartItem.query.filter_by(id=item_id, cart_id=cart.id).first_or_404()
        db.session.delete(item)
        db.session.commit()
        return cart

    @staticmethod
    def clear(user_id: int) -> Cart:
        cart = CartService.get_or_create(user_id)
        for item in list(cart.items):
            db.session.delete(item)
        db.session.commit()
        return cart
