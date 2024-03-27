import sys

def soma(a,b):
    return a + b

def subtracao(a,b):
    return a - b

def multiplicacao(a,b):
    return a * b

def divisao(a,b):
    return a / b

args = sys.argv[1:]

if len(args) > 0:
    operacao = args[0]
    match operacao:
        case "soma":
            a = int(args[1])
            b = int(args[2])
            print(soma(a,b))
        case "subtracao":
            a = int(args[1])
            b = int(args[2])
            print(subtracao(a,b))
        case "multiplicacao":
            a = int(args[1])
            b = int(args[2])
            print(multiplicacao(a,b))
        case "divisao":
            a = int(args[1])
            b = int(args[2])
            if b != 0:
                print(divisao(a,b))