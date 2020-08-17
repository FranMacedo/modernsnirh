# from django.test import TestCase, Client
# from django.urls import reverse
# from dashboard.models import Project, Category, Expense
# import json


# class TestViews(TestCase):
#     def setUp(self):
#         self.client = Client()
#         self.list_url = reverse('list')
#         self.detail_url = reverse('detail', args=['project1'])
#         self.project1 = Project.objects.create(
#             name='project1',
#             budget=1000
#         )
#         self.category1 = Category.objects.create(
#             project=self.project1,
#             name='development'
#         )

#     def test_project_list_GET(self):

#         response = self.client.get(self.list_url)

#         self.assertEquals(response.status_code, 200)
#         self.assertTemplateUsed(response, 'budget/project-list.html')

#     def test_project_detail_GET(self):

#         response = self.client.get(self.detail_url)

#         self.assertEquals(response.status_code, 200)
#         self.assertTemplateUsed(response, 'budget/project-detail.html')

#     def test_project_detail_POST_add_new_expense(self):

#         response = self.client.post(self.detail_url, {
#             'title': 'expense1',
#             'amount': 1000,
#             'category': 'development'
#         })

#         self.assertEquals(response.status_code, 302)
#         self.assertEquals(self.project1.expenses.first().title, 'expense1')

#     def test_project_detail_POST_add_no_data(self):

#         response = self.client.post(self.detail_url)

#         self.assertEquals(response.status_code, 302)
#         self.assertEquals(self.project1.expenses.count(), 0)

#     def test_project_detail_DELETE_deletes_expense(self):
#         Expense.objects.create(
#             project=self.project1,
#             title='expense1',
#             amount=1000,
#             category=self.category1
#         )

#         response = self.client.delete(self.detail_url, json.dumps({
#             'id': 1
#         }))
#         self.assertEquals(response.status_code, 204)
#         self.assertEquals(self.project1.expenses.count(), 0)

#     def test_project_detail_DELETE_no_id(self):
#         Expense.objects.create(
#             project=self.project1,
#             title='expense1',
#             amount=1000,
#             category=self.category1
#         )

#         response = self.client.delete(self.detail_url)
#         self.assertEquals(response.status_code, 404)
#         self.assertEquals(self.project1.expenses.count(), 1)

#     def test_project_create_POST(self):
#         url = reverse('add')
#         response = self.client.post(url, {
#             'name': 'project2',
#             'budget': 20000,
#             'categoriesString': 'design,development'
#         })

#         project2 = Project.objects.get(id=2)

#         self.assertEquals(project2.name, 'project2')

#         firstCategory = Category.objects.get(id=2)
#         self.assertEquals(firstCategory.project, project2)
#         self.assertEquals(firstCategory.name, 'design')

#         secondCategory = Category.objects.get(id=3)
#         self.assertEquals(secondCategory.project, project2)
#         self.assertEquals(secondCategory.name, 'development')