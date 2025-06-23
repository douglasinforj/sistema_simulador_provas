from django.contrib import admin
from .models import Questao, Alternativa, Prova, EscolhaCandidato, Categoria, Topico, Subtopico

class AlternativaInline(admin.TabularInline):
    model = Alternativa
    extra = 4
    fields = ('texto', 'is_correct')

class QuestaoAdmin(admin.ModelAdmin):
    inlines = [AlternativaInline]
    list_display = ('enunciado', 'categoria', 'created_at')
    search_fields = ('enunciado','categoria__nome')
    list_filter = ('categoria',)

class ProvaAdmin(admin.ModelAdmin):
    list_display = ('candidato_nome', 'candidato_cpf', 'categoria', 'nota', 'data_realizacao','uuid')
    search_fields = ('candidato_nome', 'candidato_cpf', 'candidato_email')
    list_filter = ('categoria',)

class SubtopicoInline(admin.TabularInline):
    model = Subtopico
    extra = 3

class TopicoAdmin(admin.ModelAdmin):
    inlines = [SubtopicoInline]
    list_display = ['nome', 'categoria']
    list_filter = ['categoria']


admin.site.register(Categoria)
admin.site.register(Questao, QuestaoAdmin)
admin.site.register(Prova, ProvaAdmin)
admin.site.register(EscolhaCandidato)
admin.site.register(Topico, TopicoAdmin)
admin.site.register(Subtopico)