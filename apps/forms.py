from django import forms

class ArticleForm(forms.Form):
    body = forms.CharField(required=True,label="文本")
    class Meta:
        fields = ['body']

class CategoryForm(forms.Form):
    category = forms.CharField(required=True,label="类别")
    class Meta:
        fields = ['category']