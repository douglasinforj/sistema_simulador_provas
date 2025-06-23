from django.db import models
import uuid

class Categoria(models.Model):
    nome = models.CharField(max_length=100)

    def __str__(self):
        return self.nome

class Topico(models.Model):
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, related_name='topicos')
    nome = models.CharField(max_length=200)
    descricao = models.TextField(blank=True, help_text="Descrição geral do tópico")
    def __str__(self):
        return self.nome
    
class Subtopico(models.Model):
    topico = models.ForeignKey(Topico, on_delete=models.CASCADE, related_name='subtopicos')
    nome = models.CharField(max_length=200)
    texto_teorico = models.TextField(help_text="Conteúdo teórico detalhado do subtema")
    def __str__(self):
        return f"{self.topico.nome} - {self.nome}"



class Questao(models.Model):
    enunciado = models.TextField()
    imagem = models.ImageField(upload_to='questoes/', blank=True, null=True)
    categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Questão"  # Optional: Human-readable singular name
        verbose_name_plural = "Questões" 

    def __str__(self):
        return self.enunciado[:50]

class Alternativa(models.Model):
    questao = models.ForeignKey(Questao, on_delete=models.CASCADE, related_name='alternativas')
    texto = models.TextField()
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.texto[:50]

class Prova(models.Model):
    candidato_nome = models.CharField(max_length=200)
    candidato_cpf = models.CharField(max_length=14)
    candidato_email = models.EmailField()
    candidato_telefone = models.CharField(max_length=15)
    categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True)
    questoes = models.ManyToManyField(Questao)
    nota = models.FloatField(null=True, blank=True)
    data_realizacao = models.DateTimeField(auto_now_add=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    tempo_limite = models.IntegerField(default=3600)  # 1 hora em segundos

    def calcular_nota(self):
        total_questoes = self.questoes.count()
        if total_questoes == 0:
            return 0
        acertos = 0
        for questao in self.questoes.all():
            respostas_corretas = set(questao.alternativas.filter(is_correct=True).values_list('id', flat=True))
            escolhas_candidato = set(EscolhaCandidato.objects.filter(prova=self, alternativa__questao=questao).values_list('alternativa_id', flat=True))
            if escolhas_candidato == respostas_corretas and escolhas_candidato:
                acertos += 1
        return (acertos / total_questoes) * 10

    def __str__(self):
        return f"Prova de {self.candidato_nome} - {self.data_realizacao}"
    
    class Meta:
        unique_together = ('candidato_cpf', 'categoria')
    

class EscolhaCandidato(models.Model):
    prova = models.ForeignKey(Prova, on_delete=models.CASCADE)
    alternativa = models.ForeignKey(Alternativa, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('prova', 'alternativa')