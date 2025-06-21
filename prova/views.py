from django.shortcuts import render, redirect, get_object_or_404
import re
from django.contrib import messages
from .models import Categoria, Questao, Prova, Alternativa, EscolhaCandidato
import random
from django.db import IntegrityError
from django.contrib.auth.decorators import login_required
from django.template.loader import render_to_string
from django.http import HttpResponse

#Emitir certificado:

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from io import BytesIO
from reportlab.lib import colors

from reportlab.lib.utils import ImageReader
from datetime import datetime
import os
from django.conf import settings



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

        questoes_selecionadas = random.sample(questoes, 8)
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


@login_required
def ranking(request):
    provas = Prova.objects.all().order_by('-nota', 'data_realizacao')
    return render(request, 'prova/ranking.html', {'provas': provas})


@login_required
def administrador(request):
    return render(request, 'prova/administrator.html')

@login_required
def emitir_certificado(request, prova_uuid):
    prova = get_object_or_404(Prova, uuid=prova_uuid)
    
    # Formatando a data em português
    meses = {
        1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril', 5: 'Maio', 6: 'Junho',
        7: 'Julho', 8: 'Agosto', 9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'
    }
    data_formatada = prova.data_realizacao.strftime("%d de {} de %Y").format(meses[prova.data_realizacao.month])

    if 'pdf' in request.GET:
        buffer = BytesIO()
        # Configurar página em paisagem (inverter width e height de A4)
        width, height = A4
        p = canvas.Canvas(buffer, pagesize=(height, width))  # Paisagem
        canvas_width, canvas_height = height, width  # A4 em paisagem: 841 x 595 pontos

        # Bordas decorativas
        p.setStrokeColor(colors.gold)
        p.setLineWidth(2)
        p.rect(1 * cm, 1 * cm, canvas_width - 2 * cm, canvas_height - 2 * cm)

        # Logotipo
        logo_path = os.path.join(settings.STATIC_ROOT or settings.STATICFILES_DIRS[0], 'images', 'cisco.png')
        if os.path.exists(logo_path):
            logo = ImageReader(logo_path)
            p.drawImage(logo, (canvas_width - 3 * cm) / 2, canvas_height - 5 * cm, width=3 * cm, height=3 * cm, preserveAspectRatio=True)

        # Título
        p.setFont("Times-Bold", 28)
        p.setFillColor(colors.darkblue)
        p.drawCentredString(canvas_width / 2, canvas_height - 8 * cm, "CERTIFICADO DE CONCLUSÃO")

        # Subtítulo
        p.setFont("Times-Roman", 16)
        p.setFillColor(colors.black)
        p.drawCentredString(canvas_width / 2, canvas_height - 10 * cm, "Provas")

        # Texto principal
        p.setFont("Times-Roman", 14)
        texto = (
            f"Certificamos que {prova.candidato_nome}, portador do CPF {prova.candidato_cpf}, "
            f"concluiu com êxito a prova da categoria {prova.categoria.nome}, "
            f"obtendo a nota {prova.nota:.2f} em avaliação realizada em {data_formatada}. "
            f"Este certificado atesta a participação e desempenho do candidato, "
            f"com carga horária de 4 horas."
        )
        # Dividir o texto em linhas para centralizar
        linhas = []
        current_line = ""
        words = texto.split()
        max_width = canvas_width - 4 * cm  # Margem de 2 cm de cada lado
        for word in words:
            test_line = current_line + " " + word if current_line else word
            if p.stringWidth(test_line, "Times-Roman", 14) <= max_width:
                current_line = test_line
            else:
                linhas.append(current_line)
                current_line = word
        if current_line:
            linhas.append(current_line)
        
        y = canvas_height - 12 * cm
        for linha in linhas:
            p.drawCentredString(canvas_width / 2, y, linha.strip())
            y -= 0.8 * cm

        # Assinaturas
        p.setFont("Times-Roman", 12)
        p.drawCentredString(canvas_width / 4, 5 * cm, "___________________________")
        p.drawCentredString(canvas_width / 4, 4 * cm, "Diretor Acadêmico")
        p.drawCentredString(3 * canvas_width / 4, 5 * cm, "___________________________")
        p.drawCentredString(3 * canvas_width / 4, 4 * cm, "Coordenador do Curso")

        # Número do certificado
        p.setFont("Times-Italic", 10)
        p.drawString(2 * cm, 2 * cm, f"Número do Certificado: {prova.uuid}")

        p.showPage()
        p.save()
        buffer.seek(0)
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="certificado_{prova.candidato_cpf}.pdf"'
        response.write(buffer.getvalue())
        buffer.close()
        return response

    context = {
        'prova': prova,
        'data_formatada': data_formatada,
    }
    html_string = render_to_string('prova/certificado.html', context)
    response = HttpResponse(content_type='text/html')
    response.write(html_string)
    return response


@login_required
def reports(request):
    # Calcular índice de acertos por categoria
    categorias = Categoria.objects.all()
    data = []
    for categoria in categorias:
        provas = Prova.objects.filter(categoria=categoria)
        total_respostas = 0
        respostas_corretas = 0
        for prova in provas:
            escolhas = EscolhaCandidato.objects.filter(prova=prova)
            total_respostas += escolhas.count()
            respostas_corretas += escolhas.filter(alternativa__is_correct=True).count()
        indice = (respostas_corretas / total_respostas * 100) if total_respostas > 0 else 0
        data.append({
            'categoria': categoria.nome,
            'indice': round(indice, 2)
        })
    
    context = {
        'data': data
    }
    return render(request, 'prova/reports.html', context)
    
