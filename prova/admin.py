from django.contrib import admin
from .models import Questao, Alternativa, Prova, Resposta, Categoria

class AlternativaInline(admin.TabularInline):
    model = Alternativa
    extra = 4

class QuestaoAdmin(admin.ModelAdmin):
    inlines = [AlternativaInline]
    list_display = ('enunciado', 'categoria', 'created_at')
    search_fields = ('enunciado',)
    list_filter = ('categoria',)

class ProvaAdmin(admin.ModelAdmin):
    list_display = ('candidato_nome', 'candidato_cpf', 'nota', 'data_realizacao')
    search_fields = ('candidato_nome', 'candidato_cpf', 'candidato_email')


admin.site.register(Categoria)
admin.site.register(Questao, QuestaoAdmin)
admin.site.register(Prova, ProvaAdmin)
admin.site.register(Resposta)