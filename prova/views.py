from django.shortcuts import render, redirect
import re
from django.contrib import messages
from .models import Categoria, Questao, Prova
import random

def validar_cpf(cpf):
    cpf = re.sub(r'\D', '', cpf)
    if len(cpf) != 11 or not cpf.isdigit():
        return False
    def calcular_digito(cpf, digitos):
        soma = sum(int(cpf[i]) * (digitos - i) for i in range(digitos - 1))
        resto = soma % 11
        return 0 if resto < 2 else 11 - resto
    digito1 = calcular_digito(cpf, 10)
    digito2 = calcular_digito(cpf + str(digito1), 11)
    return cpf[-2:] == f"{digito1}{digito2}"


def iniciar_prova(request):
    if request.method == 'POST':
        candidato_nome = request.POST['nome']
        candidato_cpf = request.POST['cpf']
        candidato_email = request.POST['email']
        candidato_telefone = request.POST['telefone']
        quantidade_questoes = int(request.POST['quantidade_questoes'])
        categoria_id = request.POST.get('categoria')

        if not validar_cpf(candidato_cpf):
            messages.error(request, 'CPF inválido.')
            return render(request, 'prova/iniciar_prova.html', {'categorias': Categoria.objects.all()})
        
        questoes = Questao.objects.all()
        if categoria_id:
            questoes = questoes.filter(categoria_id=categoria_id)
        questoes = list(questoes)
        if len(questoes) < quantidade_questoes:
            messages.error(request, 'Não há questões suficientes na categoria selecionada.')
            return render(request, 'prova/iniciar_prova.html', {'categoria': Categoria.objects.all()} )
        
        questoes_selecionadas = random.sample(questoes, quantidade_questoes)
        prova = Prova.objects.create(
            candidato_nome=candidato_nome,
            candidato_cpf=candidato_cpf,
            candidato_email=candidato_email,
            candidato_telefone=candidato_telefone,
        )
        prova.questoes.set(questoes_selecionadas)
        return redirect('realizar_prova', prova_uuid=prova.uuid)

    return render(request, 'prova/iniciar_prova.html', {'categorias': Categoria.objects.all()})
            

