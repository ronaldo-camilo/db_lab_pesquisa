import pandas as pd
from datetime import datetime
from django.utils import timezone
from .models import Paciente, ConflitoDados


def detectar_tipo_planilha(df):
    """
    Detecta automaticamente o tipo de planilha com base nas colunas.
    """
    colunas = set(df.columns)
    
    # Colunas características de cada tipo
    amostras_cols = {'Amostra_biologica', 'Sangue', 'Plasma', 'Soro', 'DNA', 'RNA'}
    bioinfo_cols = {'Metiloma', 'DNAm_gene', 'Exoma', 'RNA_Seq', 'miRNA', 'PRS'}
    clinicos_cols = {'Historico_materno', 'CARS', 'QI', 'ADI_total', 'CBCL_Internal'}
    
    # Conta quantas colunas características tem de cada tipo
    score_amostras = len(colunas & amostras_cols)
    score_bioinfo = len(colunas & bioinfo_cols)
    score_clinicos = len(colunas & clinicos_cols)
    
    if score_amostras >= score_bioinfo and score_amostras >= score_clinicos:
        return 'amostras'
    elif score_bioinfo >= score_clinicos:
        return 'bioinformatica'
    else:
        return 'dados_clinicos'


def normalizar_data(valor):
    """
    Converte diversos formatos de data para objeto date do Python.
    """
    if pd.isna(valor) or valor is None:
        return None
    
    if isinstance(valor, datetime):
        return valor.date()
    
    if isinstance(valor, pd.Timestamp):
        return valor.date()
    
    if isinstance(valor, str):
        # Tenta vários formatos comuns
        formatos = ['%Y-%m-%d', '%d/%m/%Y', '%d-%m-%Y', '%Y/%m/%d']
        for formato in formatos:
            try:
                return datetime.strptime(valor, formato).date()
            except ValueError:
                continue
    
    return None


def normalizar_valor(valor):
    """
    Normaliza valores NaN, None, strings vazias para None.
    """
    if pd.isna(valor) or valor is None or valor == '':
        return None
    
    if isinstance(valor, str):
        valor = valor.strip()
        if valor == '':
            return None
    
    return str(valor)


def mapear_colunas_amostras(row):
    """
    Mapeia colunas da planilha Amostras Biológicas para o modelo.
    """
    return {
        'nome_paciente': normalizar_valor(row.get('Nome paciente')),
        'data_nascimento': normalizar_data(row.get('Data de nascimento')),
        'nome_mae': normalizar_valor(row.get('Nome da mãe')),
        'id_projeto': normalizar_valor(row.get('ID_Projeto')),
        'sexo': normalizar_valor(row.get('Sexo')),
        'rg': normalizar_valor(row.get('RG')),
        'cpf': normalizar_valor(row.get('CPF')),
        'cid10': normalizar_valor(row.get('CID10')),
        'data_nascimento_mae': normalizar_data(row.get('Data de nascimento da mãe')),
        'id_familiar': normalizar_valor(row.get('ID_Familiar')),
        'id_lpc_biob': normalizar_valor(row.get('ID_LPC_BIOB')),
        'amostra_biologica': normalizar_valor(row.get('Amostra_biologica')),
        'sangue': normalizar_valor(row.get('Sangue')),
        'plasma': normalizar_valor(row.get('Plasma')),
        'soro': normalizar_valor(row.get('Soro')),
        'pax_gene': normalizar_valor(row.get('PaxGene')),
        'saliva': normalizar_valor(row.get('Saliva')),
        'scu': normalizar_valor(row.get('SCU')),
        'placenta': normalizar_valor(row.get('Placenta')),
        'placenta_ffpe': normalizar_valor(row.get('Placenta_FFPE')),
        'dna': normalizar_valor(row.get('DNA')),
        'rna': normalizar_valor(row.get('RNA')),
        'proteina': normalizar_valor(row.get('Proteína'))
    }


def mapear_colunas_bioinfo(row):
    """
    Mapeia colunas da planilha Bioinformática para o modelo.
    """
    return {
        'nome_paciente': normalizar_valor(row.get('Nome paciente')),
        'data_nascimento': normalizar_data(row.get('Data de nascimento')),
        'nome_mae': normalizar_valor(row.get('Nome da mãe')),
        'id_projeto': normalizar_valor(row.get('ID_Projeto')),
        'sexo': normalizar_valor(row.get('Sexo')),
        'data_nascimento_mae': normalizar_data(row.get('Data de nascimento da mãe')),
        'metiloma': normalizar_valor(row.get('Metiloma')),
        'dnam_gene': normalizar_valor(row.get('DNAm_gene')),
        'dna_seq': normalizar_valor(row.get('DNA_Seq')),
        'exoma': normalizar_valor(row.get('Exoma')),
        'rna_seq': normalizar_valor(row.get('RNA_Seq')),
        'mi_rna': normalizar_valor(row.get('miRNA')),
        'comprimento_telomerico': normalizar_valor(row.get('Comprimento_telomerico')),
        'citocinas': normalizar_valor(row.get('Citocinas')),
        'cortisol': normalizar_valor(row.get('Cortisol')),
        'exossomos': normalizar_valor(row.get('Exossomos')),
        'prs': normalizar_valor(row.get('PRS')),
        'outros_bioinfo': normalizar_valor(row.get('Outros'))
    }


def mapear_colunas_clinicos(row):
    """
    Mapeia colunas da planilha Dados Clínicos para o modelo.
    """
    return {
        'nome_paciente': normalizar_valor(row.get('Nome paciente')),
        'data_nascimento': normalizar_data(row.get('Data de nascimento')),
        'nome_mae': normalizar_valor(row.get('Nome da mãe')),
        'id_unico': normalizar_valor(row.get('ID_Unico')),
        'projeto_original': normalizar_valor(row.get('Projeto_originall')),
        'id_projeto': normalizar_valor(row.get('ID_Projeto')),
        'sexo': normalizar_valor(row.get('Sexo')),
        'rg': normalizar_valor(row.get('RG')),
        'cpf': normalizar_valor(row.get('CPF')),
        'cid10': normalizar_valor(row.get('CID10')),
        'data_nascimento_mae': normalizar_data(row.get('Data de nascimento da mãe')),
        'id_familiar': normalizar_valor(row.get('ID_Familiar')),
        'historico_materno': normalizar_valor(row.get('Historico_materno')),
        'historico_gravidez': normalizar_valor(row.get('Historico_gravidez')),
        'historico_familiar': normalizar_valor(row.get('Historico_familiar')),
        'info_parto': normalizar_valor(row.get('Info_parto')),
        'cars': normalizar_valor(row.get('CARS')),
        'qi': normalizar_valor(row.get('QI')),
        'comunicacao_vineland': normalizar_valor(row.get('comunicação_Vineland')),
        'hab_dia_vineland': normalizar_valor(row.get('Hab.dia a dia_Vineland')),
        'socializacao_vineland': normalizar_valor(row.get('Socialização_Vineland')),
        'adi_total': normalizar_valor(row.get('ADI_total')),
        'cbcl_internal': normalizar_valor(row.get('CBCL_Internal')),
        'cbcl_external': normalizar_valor(row.get('CBCL_External')),
        'score_psiquiatrico_mae': normalizar_valor(row.get('Score_Psiquiatruci_mãe')),
        'score_exposicao_ambiental': normalizar_valor(row.get('Score exposição ambiental na gestação')),
        'score_estresse_materno': normalizar_valor(row.get('Score estresse materno')),
        'escolaridade_materna': normalizar_valor(row.get('Escolaridade materna')),
        'renda_familiar': normalizar_valor(row.get('Renda familiar'))
    }


def processar_linha(dados, criar_conflitos=True):
    """
    Processa uma linha de dados e retorna:
    - 'novo': paciente foi criado
    - 'atualizado': paciente existente foi atualizado
    - 'conflito': há conflitos que precisam ser resolvidos
    - 'erro': erro ao processar
    """
    try:
        # Verifica se os campos obrigatórios estão presentes
        if not all([dados.get('nome_paciente'), dados.get('data_nascimento'), dados.get('nome_mae')]):
            return {'status': 'erro', 'mensagem': 'Campos obrigatórios ausentes'}
        
        # Busca duplicata
        paciente_existente = Paciente.buscar_duplicata(
            dados['nome_paciente'],
            dados['data_nascimento'],
            dados['nome_mae']
        )
        
        if not paciente_existente:
            # Caso Negativo: Criar novo paciente
            paciente = Paciente.objects.create(**dados)
            return {
                'status': 'novo',
                'paciente': paciente,
                'mensagem': f'Paciente {paciente.nome_paciente} cadastrado com sucesso'
            }
        
        # Caso Positivo ou Especial: Paciente já existe
        conflitos_encontrados = []
        campos_atualizados = []
        
        for campo, valor_novo in dados.items():
            if campo in ['nome_paciente', 'data_nascimento', 'nome_mae']:
                # Pula os campos de identificação
                continue
            
            valor_existente = getattr(paciente_existente, campo, None)
            
            # Se o valor novo é None ou vazio, não faz nada
            if valor_novo is None or valor_novo == '':
                continue
            
            # Se o campo existente está vazio, preenche
            if valor_existente is None or valor_existente == '':
                setattr(paciente_existente, campo, valor_novo)
                campos_atualizados.append(campo)
            
            # Se os valores são diferentes, cria conflito
            elif str(valor_existente) != str(valor_novo):
                if criar_conflitos:
                    conflito = ConflitoDados.objects.create(
                        paciente=paciente_existente,
                        campo=campo,
                        valor_existente=str(valor_existente),
                        valor_novo=str(valor_novo),
                        status='novo'
                    )
                    conflitos_encontrados.append(conflito)
        
        if campos_atualizados:
            paciente_existente.save()
        
        if conflitos_encontrados:
            return {
                'status': 'conflito',
                'paciente': paciente_existente,
                'conflitos': conflitos_encontrados,
                'mensagem': f'{len(conflitos_encontrados)} conflito(s) encontrado(s)'
            }
        
        return {
            'status': 'atualizado',
            'paciente': paciente_existente,
            'campos_atualizados': campos_atualizados,
            'mensagem': f'{len(campos_atualizados)} campo(s) atualizado(s)'
        }
    
    except Exception as e:
        return {
            'status': 'erro',
            'mensagem': f'Erro ao processar: {str(e)}'
        }


def importar_planilha(arquivo, tipo_planilha='auto', criar_conflitos=True):
    """
    Importa uma planilha Excel ou CSV.
    Retorna estatísticas da importação.
    """
    # Lê o arquivo
    if arquivo.name.endswith('.csv'):
        df = pd.read_csv(arquivo)
    else:
        df = pd.read_excel(arquivo)
    
    # Detecta o tipo se for 'auto'
    if tipo_planilha == 'auto':
        tipo_planilha = detectar_tipo_planilha(df)
    
    # Escolhe a função de mapeamento
    mapear_funcoes = {
        'amostras': mapear_colunas_amostras,
        'bioinformatica': mapear_colunas_bioinfo,
        'dados_clinicos': mapear_colunas_clinicos,
    }
    
    mapear = mapear_funcoes.get(tipo_planilha)
    if not mapear:
        return {
            'erro': f'Tipo de planilha inválido: {tipo_planilha}'
        }
    
    # Processa cada linha
    resultados = {
        'total': len(df),
        'novos': 0,
        'atualizados': 0,
        'conflitos': 0,
        'erros': 0,
        'detalhes': [],
        'conflitos_lista': []
    }
    
    for idx, row in df.iterrows():
        dados = mapear(row)
        resultado = processar_linha(dados, criar_conflitos)
        
        resultados['detalhes'].append({
            'linha': idx + 2,  # +2 porque começa do 0 e tem cabeçalho
            'resultado': resultado
        })
        
        if resultado['status'] == 'novo':
            resultados['novos'] += 1
        elif resultado['status'] == 'atualizado':
            resultados['atualizados'] += 1
        elif resultado['status'] == 'conflito':
            resultados['conflitos'] += 1
            resultados['conflitos_lista'].extend(resultado.get('conflitos', []))
        else:
            resultados['erros'] += 1
    
    return resultados

