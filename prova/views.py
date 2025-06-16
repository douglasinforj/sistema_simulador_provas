from django.shortcuts import render
import re

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
