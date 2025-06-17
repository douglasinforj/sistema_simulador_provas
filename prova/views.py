from django.shortcuts import render, redirect, get_object_or_404
import re
from django.contrib import messages
from .models import Categoria, Questao, Prova, Alternativa, EscolhaCandidato
import random
from django.db import IntegrityError

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
        categoria_id = request.POST['categoria']

        if not validar_cpf(candidato_cpf):
            messages.error(request, 'CPF inválido.')
            return render(request, 'prova/iniciar_prova.html', {'categorias': Categoria.objects.all()})

        try:
            categoria = Categoria.objects.get(id=categoria_id)
        except Categoria.DoesNotExist:
            messages.error(request, 'Categoria inválida.')
            return render(request, 'prova/iniciar_prova.html', {'categorias': Categoria.objects.all()})

        # Verificar se o CPF já foi usado para esta categoria
        if Prova.objects.filter(candidato_cpf=candidato_cpf, categoria=categoria).exists():
            messages.error(request, 'Este CPF já foi usado para uma prova nesta categoria.')
            return render(request, 'prova/iniciar_prova.html', {'categorias': Categoria.objects.all()})

        questoes = list(Questao.objects.filter(categoria=categoria))
        if len(questoes) < 4:
            messages.error(request, 'Não há questões suficientes na categoria selecionada.')
            return render(request, 'prova/iniciar_prova.html', {'categorias': Categoria.objects.all()})

        questoes_selecionadas = random.sample(questoes, 4)
        try:
            prova = Prova.objects.create(
                candidato_nome=candidato_nome,
                candidato_cpf=candidato_cpf,
                candidato_email=candidato_email,
                candidato_telefone=candidato_telefone,
                categoria=categoria,
            )
            prova.questoes.set(questoes_selecionadas)
            return redirect('realizar_prova', prova_uuid=prova.uuid)
        except IntegrityError:
            messages.error(request, 'Este CPF já foi usado para uma prova nesta categoria.')
            return render(request, 'prova/iniciar_prova.html', {'categorias': Categoria.objects.all()})

    return render(request, 'prova/iniciar_prova.html', {'categorias': Categoria.objects.all()})
            

def realizar_prova(request, prova_uuid):
    prova = get_object_or_404(Prova, uuid=prova_uuid)
    if request.method == 'POST':
        for questao in prova.questoes.all():
            respostas_selecionadas = request.POST.getlist(f'questao_{questao.id}')
            for alternativa_id in respostas_selecionadas:
                alternativa = Alternativa.objects.get(id=alternativa_id)
                EscolhaCandidato.objects.create(prova=prova, alternativa=alternativa)
        prova.nota = prova.calcular_nota()
        prova.save()
        return redirect('resultado_prova', prova_uuid=prova.uuid)

    questoes = prova.questoes.all()
    return render(request, 'prova/realizar_prova.html', {'prova': prova, 'questoes': questoes, 'tempo_limite': prova.tempo_limite})


def resultado_prova(request, prova_uuid):
    prova = get_object_or_404(Prova, uuid=prova_uuid)
    return render(request, 'prova/resultado_prova.html', {'prova': prova})

