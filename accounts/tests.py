from django.test import TestCase
from django.contrib import admin
from django.urls import reverse
from accounts.forms import AccountChangeForm, AccountCreationForm
from accounts.admin import UserProfileAdmin
from accounts.models import Account, UserProfile
from carts.models import Cart, CartItem
from category.models import Category
from store.models import Product, ProductVariation


class AccountAdminFormTests(TestCase):
	def test_account_creation_form_hashes_password(self):
		form = AccountCreationForm(
			data={
				'email': 'adminuser@example.com',
				'username': 'adminuser',
				'first_name': 'Admin',
				'last_name': 'User',
				'phone_number': '9999999999',
				'password1': 'VeryStrongPass123!',
				'password2': 'VeryStrongPass123!',
			}
		)

		self.assertTrue(form.is_valid(), form.errors)
		user = form.save()
		self.assertNotEqual(user.password, 'VeryStrongPass123!')
		self.assertTrue(user.check_password('VeryStrongPass123!'))

	def test_account_creation_form_requires_matching_passwords(self):
		form = AccountCreationForm(
			data={
				'email': 'mismatch@example.com',
				'username': 'mismatch',
				'first_name': 'Mismatch',
				'last_name': 'Case',
				'phone_number': '8888888888',
				'password1': 'VeryStrongPass123!',
				'password2': 'DifferentPass123!',
			}
		)

		self.assertFalse(form.is_valid())
		self.assertIn('password2', form.errors)

	def test_account_change_form_keeps_existing_password_hash(self):
		user = Account.objects.create_user(
			first_name='Jane',
			last_name='Doe',
			username='janedoe',
			email='jane@example.com',
			phone_number='7777777777',
			password='OriginalPass123!',
		)

		original_hash = user.password

		form = AccountChangeForm(
			data={
				'email': user.email,
				'username': user.username,
				'first_name': 'Janet',
				'last_name': user.last_name,
				'phone_number': user.phone_number,
				'password': original_hash,
				'is_active': user.is_active,
				'is_staff': user.is_staff,
				'is_admin': user.is_admin,
				'is_superadmin': user.is_superadmin,
			},
			instance=user,
		)

		self.assertTrue(form.is_valid(), form.errors)
		updated_user = form.save()
		self.assertEqual(updated_user.password, original_hash)
		self.assertTrue(updated_user.check_password('OriginalPass123!'))


class UserProfileModelTests(TestCase):
	def test_full_address_handles_blank_fields(self):
		user = Account.objects.create_user(
			first_name='Profile',
			last_name='User',
			username='profileuser',
			email='profile@example.com',
			password='Password123!',
		)
		profile = UserProfile.objects.create(user=user)

		self.assertEqual(profile.full_address(), ' ')


class UserProfileAdminTests(TestCase):
	def test_thumbnail_returns_fallback_text_when_no_image(self):
		user = Account.objects.create_user(
			first_name='No',
			last_name='Image',
			username='noimage',
			email='noimage@example.com',
			password='Password123!',
		)
		profile = UserProfile.objects.create(user=user)
		model_admin = UserProfileAdmin(UserProfile, admin.site)

		self.assertEqual(model_admin.thumbnail(profile), 'No image')

	def test_userprofile_admin_changelist_loads(self):
		Account.objects.create_superuser(
			first_name='Admin',
			last_name='User',
			email='admin@example.com',
			username='adminuser',
			password='AdminPass123!',
		)
		self.client.login(username='admin@example.com', password='AdminPass123!')

		url = reverse('admin:accounts_userprofile_changelist')
		response = self.client.get(url)

		self.assertEqual(response.status_code, 200)


class LoginCartMergeTests(TestCase):
	def setUp(self):
		self.password = 'LoginPass123!'
		self.user = Account.objects.create_user(
			first_name='Cart',
			last_name='User',
			username='cartuser',
			email='cartuser@example.com',
			password=self.password,
		)

		self.category = Category.objects.create(
			category_name='Shoes',
			slug='shoes',
		)
		self.product = Product.objects.create(
			product_name='Runner',
			slug='runner-shoe',
			description='Running shoe',
			price=100,
			images='photos/products/test.jpg',
			category=self.category,
		)
		self.variation = ProductVariation.objects.create(
			product=self.product,
			color='Black',
			size='42',
			stock=20,
		)

	def _create_guest_cart_item(self, quantity):
		session = self.client.session
		session['guest_cart'] = True
		session.save()
		cart = Cart.objects.create(cart_id=session.session_key)
		return CartItem.objects.create(
			cart=cart,
			product_variation=self.variation,
			quantity=quantity,
		)

	def test_guest_cart_item_transfers_to_user_on_login(self):
		guest_item = self._create_guest_cart_item(quantity=2)

		response = self.client.post(
			reverse('login'),
			data={'email': self.user.email, 'password': self.password},
		)

		self.assertEqual(response.status_code, 302)
		guest_item.refresh_from_db()
		self.assertEqual(guest_item.user, self.user)
		self.assertIsNone(guest_item.cart)

		user_items = CartItem.objects.filter(user=self.user, product_variation=self.variation)
		self.assertEqual(user_items.count(), 1)
		self.assertEqual(user_items.first().quantity, 2)

	def test_guest_and_user_cart_items_merge_quantities_on_login(self):
		self._create_guest_cart_item(quantity=3)
		existing_user_item = CartItem.objects.create(
			user=self.user,
			product_variation=self.variation,
			quantity=2,
		)

		response = self.client.post(
			reverse('login'),
			data={'email': self.user.email, 'password': self.password},
		)

		self.assertEqual(response.status_code, 302)
		existing_user_item.refresh_from_db()
		self.assertEqual(existing_user_item.quantity, 5)
		self.assertFalse(CartItem.objects.filter(cart__isnull=False, product_variation=self.variation).exists())
