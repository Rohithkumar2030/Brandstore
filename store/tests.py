from django.test import TestCase
from django.urls import reverse

from accounts.models import Account
from category.models import Category
from store.models import Product, ProductVariation, ReviewRating


class ProductDetailVariationVisibilityTests(TestCase):
	def setUp(self):
		self.category = Category.objects.create(
			category_name='ApparelTest',
			slug='apparel-test',
		)
		self.product = Product.objects.create(
			product_name='Test Tee',
			slug='test-tee',
			description='Test product',
			price=499,
			images='photos/products/test-tee.jpg',
			is_available=True,
			category=self.category,
		)

		ProductVariation.objects.create(
			product=self.product,
			color='Red',
			size='M',
			stock=10,
			is_active=True,
		)
		ProductVariation.objects.create(
			product=self.product,
			color='Blue',
			size='L',
			stock=10,
			is_active=False,
		)

	def test_product_detail_shows_only_active_variations(self):
		response = self.client.get(
			reverse(
				'product_detail',
				kwargs={
					'category_slug': self.category.slug,
					'product_slug': self.product.slug,
				},
			)
		)

		self.assertEqual(response.status_code, 200)
		self.assertIn('Red', list(response.context['colors']))
		self.assertIn('M', list(response.context['sizes']))
		self.assertNotIn('Blue', list(response.context['colors']))
		self.assertNotIn('L', list(response.context['sizes']))


class ProductRatingComputationTests(TestCase):
	def setUp(self):
		self.category = Category.objects.create(
			category_name='Ratings Category',
			slug='ratings-category',
		)
		self.product = Product.objects.create(
			product_name='Ratings Product',
			slug='ratings-product',
			description='Ratings test product',
			price=999,
			images='photos/products/ratings.jpg',
			is_available=True,
			category=self.category,
		)

		self.user_1 = Account.objects.create_user(
			first_name='User',
			last_name='One',
			username='userone',
			email='userone@example.com',
			password='TestPass123!',
		)
		self.user_2 = Account.objects.create_user(
			first_name='User',
			last_name='Two',
			username='usertwo',
			email='usertwo@example.com',
			password='TestPass123!',
		)
		self.user_3 = Account.objects.create_user(
			first_name='User',
			last_name='Three',
			username='userthree',
			email='userthree@example.com',
			password='TestPass123!',
		)

	def test_average_and_count_include_only_approved_reviews(self):
		ReviewRating.objects.create(
			product=self.product,
			user=self.user_1,
			subject='Good',
			review='Good product',
			rating=2.0,
			status=True,
		)
		ReviewRating.objects.create(
			product=self.product,
			user=self.user_2,
			subject='Great',
			review='Great product',
			rating=4.0,
			status=True,
		)
		ReviewRating.objects.create(
			product=self.product,
			user=self.user_3,
			subject='Hidden',
			review='Should not count',
			rating=5.0,
			status=False,
		)

		self.assertEqual(self.product.averageReview(), 3.0)
		self.assertEqual(self.product.countReview(), 2)

	def test_average_and_count_when_no_reviews(self):
		self.assertEqual(self.product.averageReview(), 0)
		self.assertEqual(self.product.countReview(), 0)


class SubmitReviewFlowTests(TestCase):
	def setUp(self):
		self.category = Category.objects.create(
			category_name='Submit Category',
			slug='submit-category',
		)
		self.product = Product.objects.create(
			product_name='Submit Product',
			slug='submit-product',
			description='Submit review test product',
			price=699,
			images='photos/products/submit-product.jpg',
			is_available=True,
			category=self.category,
		)
		self.user = Account.objects.create_user(
			first_name='Submit',
			last_name='User',
			username='submituser',
			email='submituser@example.com',
			password='SubmitPass123!',
		)

	def test_submit_review_saves_selected_rating(self):
		self.client.login(email=self.user.email, password='SubmitPass123!')
		response = self.client.post(
			reverse('submit_review', kwargs={'product_id': self.product.id}),
			data={
				'subject': 'Two stars',
				'review': 'Not great',
				'rating': '2',
			},
			HTTP_REFERER=self.product.get_url(),
		)

		self.assertEqual(response.status_code, 302)
		review = ReviewRating.objects.get(user=self.user, product=self.product)
		self.assertEqual(review.rating, 2.0)
		self.assertEqual(self.product.averageReview(), 2.0)

	def test_submit_review_updates_existing_review_rating(self):
		ReviewRating.objects.create(
			product=self.product,
			user=self.user,
			subject='Old',
			review='Old review',
			rating=5.0,
			status=True,
		)

		self.client.login(email=self.user.email, password='SubmitPass123!')
		response = self.client.post(
			reverse('submit_review', kwargs={'product_id': self.product.id}),
			data={
				'subject': 'Updated',
				'review': 'Updated review',
				'rating': '2',
			},
			HTTP_REFERER=self.product.get_url(),
		)

		self.assertEqual(response.status_code, 302)
		review = ReviewRating.objects.get(user=self.user, product=self.product)
		self.assertEqual(review.rating, 2.0)
		self.assertEqual(self.product.averageReview(), 2.0)
