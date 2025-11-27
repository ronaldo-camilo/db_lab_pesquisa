from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.db.models import Q
from django.utils import timezone
from datetime import datetime
import pandas as pd
from io import BytesIO

from .models import Paciente, ConflitoDados
from .forms import PacienteForm, UploadPlanilhaForm, ResolverConflitoForm, FiltroExportacaoForm
from .utils import importar_planilha


def index(request):
    """
    Página inicial com dashboard de estatísticas.
    """
    total_pacientes = Paciente.objects.count()
    conflitos_pendentes = ConflitoDados.objects.filter(status='novo').count()
    ultimos_cadastros = Paciente.objects.order_by('-data_cadastro')[:10]
    
    context = {
        'total_pacientes': total_pacientes,
        'conflitos_pendentes': conflitos_pendentes,
        'ultimos_cadastros': ultimos_cadastros,
    }
    
    return render(request, 'pacientes/index.html', context)


def listar_pacientes(request):
    """
    Lista todos os pacientes com opções de busca e filtro.
    Busca pelos 3 campos-chave separadamente.
    """
    pacientes = Paciente.objects.all()
    
    # Busca por Nome do Paciente
    busca_nome = request.GET.get('busca_nome', '')
    if busca_nome:
        pacientes = pacientes.filter(nome_paciente__icontains=busca_nome)
    
    # Busca por Data de Nascimento
    busca_data = request.GET.get('busca_data', '')
    if busca_data:
        pacientes = pacientes.filter(data_nascimento=busca_data)
    
    # Busca por Nome da Mãe
    busca_mae = request.GET.get('busca_mae', '')
    if busca_mae:
        pacientes = pacientes.filter(nome_mae__icontains=busca_mae)
    
    # Filtro adicional por projeto
    projeto = request.GET.get('projeto', '')
    if projeto:
        pacientes = pacientes.filter(id_projeto__icontains=projeto)
    
    # Paginação simples (top 100)
    pacientes = pacientes[:100]
    
    # Lista de projetos únicos para o filtro
    projetos = Paciente.objects.values_list('id_projeto', flat=True).distinct()
    projetos = [p for p in projetos if p]
    
    context = {
        'pacientes': pacientes,
        'busca_nome': busca_nome,
        'busca_data': busca_data,
        'busca_mae': busca_mae,
        'projeto': projeto,
        'projetos': projetos,
    }
    
    return render(request, 'pacientes/listar.html', context)


def detalhe_paciente(request, pk):
    """
    Exibe detalhes de um paciente específico.
    """
    paciente = get_object_or_404(Paciente, pk=pk)
    conflitos = ConflitoDados.objects.filter(paciente=paciente, status='novo')
    
    context = {
        'paciente': paciente,
        'conflitos': conflitos,
    }
    
    return render(request, 'pacientes/detalhe.html', context)


def criar_paciente(request):
    """
    Formulário para criar/editar paciente manualmente.
    """
    if request.method == 'POST':
        form = PacienteForm(request.POST)
        if form.is_valid():
            # Verifica duplicata
            paciente_existente = Paciente.buscar_duplicata(
                form.cleaned_data['nome_paciente'],
                form.cleaned_data['data_nascimento'],
                form.cleaned_data['nome_mae']
            )
            
            if paciente_existente:
                messages.warning(
                    request,
                    f'Paciente já cadastrado! <a href="/pacientes/{paciente_existente.pk}/">Ver cadastro</a>',
                    extra_tags='safe'
                )
                return redirect('detalhe_paciente', pk=paciente_existente.pk)
            
            paciente = form.save()
            messages.success(request, f'Paciente {paciente.nome_paciente} cadastrado com sucesso!')
            return redirect('detalhe_paciente', pk=paciente.pk)
    else:
        form = PacienteForm()
    
    context = {
        'form': form,
        'titulo': 'Cadastrar Novo Paciente'
    }
    
    return render(request, 'pacientes/formulario.html', context)


def editar_paciente(request, pk):
    """
    Edita um paciente existente.
    """
    paciente = get_object_or_404(Paciente, pk=pk)
    
    if request.method == 'POST':
        form = PacienteForm(request.POST, instance=paciente)
        if form.is_valid():
            form.save()
            messages.success(request, f'Dados de {paciente.nome_paciente} atualizados com sucesso!')
            return redirect('detalhe_paciente', pk=paciente.pk)
    else:
        form = PacienteForm(instance=paciente)
    
    context = {
        'form': form,
        'paciente': paciente,
        'titulo': f'Editar: {paciente.nome_paciente}'
    }
    
    return render(request, 'pacientes/formulario.html', context)


def upload_planilha(request):
    """
    Upload e processamento de planilhas Excel/CSV.
    """
    if request.method == 'POST':
        form = UploadPlanilhaForm(request.POST, request.FILES)
        if form.is_valid():
            arquivo = request.FILES['arquivo']
            tipo_planilha = form.cleaned_data['tipo_planilha']
            criar_conflitos = not form.cleaned_data['substituir_duplicatas']
            
            try:
                resultados = importar_planilha(arquivo, tipo_planilha, criar_conflitos)
                
                if 'erro' in resultados:
                    messages.error(request, f'Erro ao importar: {resultados["erro"]}')
                else:
                    # Armazena resultados na sessão para exibir
                    request.session['resultados_importacao'] = {
                        'total': resultados['total'],
                        'novos': resultados['novos'],
                        'atualizados': resultados['atualizados'],
                        'conflitos': resultados['conflitos'],
                        'erros': resultados['erros'],
                    }
                    
                    # Se houver conflitos, redireciona para resolver
                    if resultados['conflitos'] > 0:
                        conflitos_ids = [c.id for c in resultados['conflitos_lista']]
                        request.session['conflitos_pendentes'] = conflitos_ids
                        messages.warning(
                            request,
                            f'Importação concluída com {resultados["conflitos"]} conflito(s). Resolva os conflitos abaixo.'
                        )
                        return redirect('resolver_conflitos')
                    
                    messages.success(
                        request,
                        f'Importação concluída! Novos: {resultados["novos"]}, '
                        f'Atualizados: {resultados["atualizados"]}, '
                        f'Erros: {resultados["erros"]}'
                    )
                    return redirect('listar_pacientes')
            
            except Exception as e:
                messages.error(request, f'Erro ao processar arquivo: {str(e)}')
    else:
        form = UploadPlanilhaForm()
    
    context = {
        'form': form
    }
    
    return render(request, 'pacientes/upload.html', context)


def resolver_conflitos(request):
    """
    Interface para resolver conflitos de dados.
    """
    # Busca conflitos pendentes (da sessão ou todos)
    conflitos_ids = request.session.get('conflitos_pendentes')
    
    if conflitos_ids:
        conflitos = ConflitoDados.objects.filter(id__in=conflitos_ids, status='novo')
    else:
        conflitos = ConflitoDados.objects.filter(status='novo')[:50]  # Limita a 50 por vez
    
    if request.method == 'POST':
        for conflito in conflitos:
            escolha = request.POST.get(f'conflito_{conflito.id}')
            
            if escolha == 'existente':
                conflito.valor_escolhido = conflito.valor_existente
            elif escolha == 'novo':
                conflito.valor_escolhido = conflito.valor_novo
                # Atualiza o paciente com o novo valor
                setattr(conflito.paciente, conflito.campo, conflito.valor_novo)
                conflito.paciente.save()
            
            conflito.status = 'resolvido'
            conflito.data_resolucao = timezone.now()
            conflito.save()
        
        # Limpa a sessão
        if 'conflitos_pendentes' in request.session:
            del request.session['conflitos_pendentes']
        
        messages.success(request, f'{len(conflitos)} conflito(s) resolvido(s) com sucesso!')
        return redirect('listar_pacientes')
    
    # Agrupa conflitos por paciente
    conflitos_por_paciente = {}
    for conflito in conflitos:
        paciente_id = conflito.paciente.id
        if paciente_id not in conflitos_por_paciente:
            conflitos_por_paciente[paciente_id] = {
                'paciente': conflito.paciente,
                'conflitos': []
            }
        conflitos_por_paciente[paciente_id]['conflitos'].append(conflito)
    
    context = {
        'conflitos_por_paciente': conflitos_por_paciente.values(),
        'total_conflitos': len(conflitos)
    }
    
    return render(request, 'pacientes/resolver_conflitos.html', context)


def exportar_dados(request):
    """
    Exporta dados em formato Excel, CSV ou PDF.
    """
    if request.method == 'POST':
        form = FiltroExportacaoForm(request.POST)
        if form.is_valid():
            # Busca pacientes com filtros
            pacientes = Paciente.objects.all()
            
            # Filtro por projeto
            if form.cleaned_data.get('projeto'):
                pacientes = pacientes.filter(
                    Q(id_projeto__icontains=form.cleaned_data['projeto']) |
                    Q(projeto_original__icontains=form.cleaned_data['projeto'])
                )
            
            formato = form.cleaned_data['formato']
            campos_selecionados = form.cleaned_data.get('campos_selecionados', [])
            
            # Se nenhum campo foi selecionado, exporta todos
            if not campos_selecionados:
                campos_selecionados = None
            
            if formato == 'excel':
                return exportar_excel(pacientes, campos_selecionados)
            elif formato == 'csv':
                return exportar_csv(pacientes, campos_selecionados)
            elif formato == 'visualizar':
                return visualizar_dados(request, pacientes, campos_selecionados)
    else:
        form = FiltroExportacaoForm()
    
    context = {
        'form': form
    }
    
    return render(request, 'pacientes/exportar.html', context)


def exportar_excel(pacientes, campos_selecionados=None):
    """
    Gera arquivo Excel com os dados dos pacientes.
    Se nenhum campo selecionado, exporta apenas os 3 campos-chave.
    """
    # Mapeamento de campos internos para labels amigáveis
    campo_labels = {
        'id': 'ID',
        'nome_paciente': 'Nome Paciente',
        'data_nascimento': 'Data Nascimento',
        'nome_mae': 'Nome Mãe',
        'id_projeto': 'ID Projeto',
        'id_unico': 'ID Único',
        'projeto_original': 'Projeto Original',
        'sexo': 'Sexo',
        'rg': 'RG',
        'cpf': 'CPF',
        'cid10': 'CID10',
        'data_nascimento_mae': 'Data Nascimento Mãe',
        'id_familiar': 'ID Familiar',
        'id_lpc_biob': 'ID LPC BIOB',
        'amostra_biologica': 'Amostra Biológica',
        'sangue': 'Sangue',
        'plasma': 'Plasma',
        'soro': 'Soro',
        'pax_gene': 'PaxGene',
        'saliva': 'Saliva',
        'scu': 'SCU',
        'placenta': 'Placenta',
        'placenta_ffpe': 'Placenta FFPE',
        'dna': 'DNA',
        'rna': 'RNA',
        'proteina': 'Proteína',
        'metiloma': 'Metiloma',
        'dnam_gene': 'DNAm Gene',
        'dna_seq': 'DNA Seq',
        'exoma': 'Exoma',
        'rna_seq': 'RNA Seq',
        'mi_rna': 'miRNA',
        'comprimento_telomerico': 'Comprimento Telomérico',
        'citocinas': 'Citocinas',
        'cortisol': 'Cortisol',
        'exossomos': 'Exossomos',
        'prs': 'PRS',
        'outros_bioinfo': 'Outros (Bioinfo)',
        'historico_materno': 'Histórico Materno',
        'historico_gravidez': 'Histórico Gravidez',
        'historico_familiar': 'Histórico Familiar',
        'info_parto': 'Info Parto',
        'cars': 'CARS',
        'qi': 'QI',
        'comunicacao_vineland': 'Comunicação Vineland',
        'hab_dia_vineland': 'Hab. Dia a Dia Vineland',
        'socializacao_vineland': 'Socialização Vineland',
        'adi_total': 'ADI Total',
        'cbcl_internal': 'CBCL Internal',
        'cbcl_external': 'CBCL External',
        'score_psiquiatrico_mae': 'Score Psiquiátrico Mãe',
        'score_exposicao_ambiental': 'Score Exposição Ambiental',
        'score_estresse_materno': 'Score Estresse Materno',
        'escolaridade_materna': 'Escolaridade Materna',
        'renda_familiar': 'Renda Familiar',
        'fonte_dados': 'Fonte Dados',
        'data_cadastro': 'Data Cadastro',
        'data_atualizacao': 'Data Atualização',
    }
    
    # Define quais campos exportar
    if campos_selecionados:
        campos_exportar = ['id'] + list(campos_selecionados)
    else:
        # Se nenhum campo selecionado, exporta apenas os 3 campos-chave
        campos_exportar = ['id', 'nome_paciente', 'data_nascimento', 'nome_mae']
    
    # Prepara dados para DataFrame
    dados = []
    for p in pacientes:
        linha = {}
        for campo in campos_exportar:
            if campo == 'id':
                linha[campo_labels[campo]] = p.id
            else:
                valor = getattr(p, campo, None)
                # Formata datas
                if campo in ['data_nascimento', 'data_nascimento_mae'] and valor:
                    linha[campo_labels[campo]] = valor.strftime('%d/%m/%Y')
                elif campo in ['data_cadastro', 'data_atualizacao'] and valor:
                    linha[campo_labels[campo]] = valor.strftime('%d/%m/%Y %H:%M')
                else:
                    linha[campo_labels[campo]] = valor if valor else ''
        dados.append(linha)
    
    df = pd.DataFrame(dados)
    
    # Cria arquivo Excel em memória
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Pacientes')
    
    output.seek(0)
    
    # Retorna como resposta HTTP
    response = HttpResponse(
        output.read(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename=pacientes_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
    
    return response


def exportar_csv(pacientes, campos_selecionados=None):
    """
    Gera arquivo CSV com os dados dos pacientes.
    Se nenhum campo selecionado, exporta apenas os 3 campos-chave.
    """
    # Usa a mesma lógica do Excel para consistência
    # Mapeamento de campos internos para labels amigáveis
    campo_labels = {
        'id': 'ID',
        'nome_paciente': 'Nome Paciente',
        'data_nascimento': 'Data Nascimento',
        'nome_mae': 'Nome Mãe',
        'id_projeto': 'ID Projeto',
        'id_unico': 'ID Único',
        'projeto_original': 'Projeto Original',
        'sexo': 'Sexo',
        'rg': 'RG',
        'cpf': 'CPF',
        'cid10': 'CID10',
        'data_nascimento_mae': 'Data Nascimento Mãe',
        'id_familiar': 'ID Familiar',
        'id_lpc_biob': 'ID LPC BIOB',
        'amostra_biologica': 'Amostra Biológica',
        'sangue': 'Sangue',
        'plasma': 'Plasma',
        'soro': 'Soro',
        'pax_gene': 'PaxGene',
        'saliva': 'Saliva',
        'scu': 'SCU',
        'placenta': 'Placenta',
        'placenta_ffpe': 'Placenta FFPE',
        'dna': 'DNA',
        'rna': 'RNA',
        'proteina': 'Proteína',
        'metiloma': 'Metiloma',
        'dnam_gene': 'DNAm Gene',
        'dna_seq': 'DNA Seq',
        'exoma': 'Exoma',
        'rna_seq': 'RNA Seq',
        'mi_rna': 'miRNA',
        'comprimento_telomerico': 'Comprimento Telomérico',
        'citocinas': 'Citocinas',
        'cortisol': 'Cortisol',
        'exossomos': 'Exossomos',
        'prs': 'PRS',
        'outros_bioinfo': 'Outros (Bioinfo)',
        'historico_materno': 'Histórico Materno',
        'historico_gravidez': 'Histórico Gravidez',
        'historico_familiar': 'Histórico Familiar',
        'info_parto': 'Info Parto',
        'cars': 'CARS',
        'qi': 'QI',
        'comunicacao_vineland': 'Comunicação Vineland',
        'hab_dia_vineland': 'Hab. Dia a Dia Vineland',
        'socializacao_vineland': 'Socialização Vineland',
        'adi_total': 'ADI Total',
        'cbcl_internal': 'CBCL Internal',
        'cbcl_external': 'CBCL External',
        'score_psiquiatrico_mae': 'Score Psiquiátrico Mãe',
        'score_exposicao_ambiental': 'Score Exposição Ambiental',
        'score_estresse_materno': 'Score Estresse Materno',
        'escolaridade_materna': 'Escolaridade Materna',
        'renda_familiar': 'Renda Familiar',
        'fonte_dados': 'Fonte Dados',
        'data_cadastro': 'Data Cadastro',
        'data_atualizacao': 'Data Atualização',
    }
    
    # Define quais campos exportar
    if campos_selecionados:
        campos_exportar = ['id'] + list(campos_selecionados)
    else:
        # Se nenhum campo selecionado, exporta apenas os 3 campos-chave
        campos_exportar = ['id', 'nome_paciente', 'data_nascimento', 'nome_mae']
    
    # Prepara dados para DataFrame
    dados = []
    for p in pacientes:
        linha = {}
        for campo in campos_exportar:
            if campo == 'id':
                linha[campo_labels[campo]] = p.id
            else:
                valor = getattr(p, campo, None)
                if campo in ['data_nascimento', 'data_nascimento_mae'] and valor:
                    linha[campo_labels[campo]] = valor.strftime('%d/%m/%Y')
                elif campo in ['data_cadastro', 'data_atualizacao'] and valor:
                    linha[campo_labels[campo]] = valor.strftime('%d/%m/%Y %H:%M')
                else:
                    linha[campo_labels[campo]] = valor if valor else ''
        dados.append(linha)
    
    df = pd.DataFrame(dados)
    
    # Cria CSV em memória
    output = BytesIO()
    df.to_csv(output, index=False, encoding='utf-8-sig')
    output.seek(0)
    
    # Retorna como resposta HTTP
    response = HttpResponse(output.read(), content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename=pacientes_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    
    return response


def visualizar_dados(request, pacientes, campos_selecionados=None):
    """
    Renderiza página de visualização formatada para impressão.
    Abre em nova aba com layout paisagem.
    """
    # Mapeamento de campos internos para labels amigáveis
    campo_labels = {
        'id': 'ID',
        'nome_paciente': 'Nome Paciente',
        'data_nascimento': 'Data Nascimento',
        'nome_mae': 'Nome Mãe',
        'id_projeto': 'ID Projeto',
        'id_unico': 'ID Único',
        'projeto_original': 'Projeto Original',
        'sexo': 'Sexo',
        'rg': 'RG',
        'cpf': 'CPF',
        'cid10': 'CID10',
        'data_nascimento_mae': 'Data Nascimento Mãe',
        'id_familiar': 'ID Familiar',
        'id_lpc_biob': 'ID LPC BIOB',
        'amostra_biologica': 'Amostra Biológica',
        'sangue': 'Sangue',
        'plasma': 'Plasma',
        'soro': 'Soro',
        'pax_gene': 'PaxGene',
        'saliva': 'Saliva',
        'scu': 'SCU',
        'placenta': 'Placenta',
        'placenta_ffpe': 'Placenta FFPE',
        'dna': 'DNA',
        'rna': 'RNA',
        'proteina': 'Proteína',
        'metiloma': 'Metiloma',
        'dnam_gene': 'DNAm Gene',
        'dna_seq': 'DNA Seq',
        'exoma': 'Exoma',
        'rna_seq': 'RNA Seq',
        'mi_rna': 'miRNA',
        'comprimento_telomerico': 'Compr. Telomérico',
        'citocinas': 'Citocinas',
        'cortisol': 'Cortisol',
        'exossomos': 'Exossomos',
        'prs': 'PRS',
        'outros_bioinfo': 'Outros (Bioinfo)',
        'historico_materno': 'Histórico Materno',
        'historico_gravidez': 'Histórico Gravidez',
        'historico_familiar': 'Histórico Familiar',
        'info_parto': 'Info Parto',
        'cars': 'CARS',
        'qi': 'QI',
        'comunicacao_vineland': 'Com. Vineland',
        'hab_dia_vineland': 'Hab. Dia Vineland',
        'socializacao_vineland': 'Soc. Vineland',
        'adi_total': 'ADI Total',
        'cbcl_internal': 'CBCL Internal',
        'cbcl_external': 'CBCL External',
        'score_psiquiatrico_mae': 'Score Psiq. Mãe',
        'score_exposicao_ambiental': 'Score Exp. Amb.',
        'score_estresse_materno': 'Score Estresse Mat.',
        'escolaridade_materna': 'Escolaridade Mat.',
        'renda_familiar': 'Renda Familiar',
        'fonte_dados': 'Fonte Dados',
        'data_cadastro': 'Data Cadastro',
        'data_atualizacao': 'Data Atualização',
    }
    
    # Define quais campos exibir
    if campos_selecionados:
        campos_exibir = ['id'] + list(campos_selecionados)
    else:
        # Se nenhum campo selecionado, exibe apenas os 3 campos-chave
        campos_exibir = ['id', 'nome_paciente', 'data_nascimento', 'nome_mae']
    
    # Prepara cabeçalhos
    cabecalhos = [campo_labels.get(campo, campo) for campo in campos_exibir]
    
    # Prepara dados
    dados_tabela = []
    for p in pacientes:
        linha = []
        for campo in campos_exibir:
            if campo == 'id':
                valor = p.id
            else:
                valor = getattr(p, campo, None)
                # Formata datas
                if campo in ['data_nascimento', 'data_nascimento_mae'] and valor:
                    valor = valor.strftime('%d/%m/%Y')
                elif campo in ['data_cadastro', 'data_atualizacao'] and valor:
                    valor = valor.strftime('%d/%m/%Y %H:%M')
                # Limita tamanho de textos longos
                elif isinstance(valor, str) and len(valor) > 50:
                    valor = valor[:47] + '...'
            linha.append(valor if valor else '-')
        dados_tabela.append(linha)
    
    context = {
        'cabecalhos': cabecalhos,
        'dados': dados_tabela,
        'total_registros': len(dados_tabela),
        'total_campos': len(cabecalhos),
        'data_geracao': datetime.now(),
    }
    
    return render(request, 'pacientes/visualizar.html', context)


def deletar_paciente(request, pk):
    """
    Deleta um paciente (com confirmação).
    """
    paciente = get_object_or_404(Paciente, pk=pk)
    
    if request.method == 'POST':
        nome = paciente.nome_paciente
        paciente.delete()
        messages.success(request, f'Paciente {nome} deletado com sucesso!')
        return redirect('listar_pacientes')
    
    context = {
        'paciente': paciente
    }
    
    return render(request, 'pacientes/confirmar_deletar.html', context)
