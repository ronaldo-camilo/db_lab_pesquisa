from django import forms
from .models import Paciente, ConflitoDados


class PacienteForm(forms.ModelForm):
    """
    Formulário para entrada manual de dados de paciente.
    """
    class Meta:
        model = Paciente
        fields = [
            # Campos principais
            'nome_paciente', 'data_nascimento', 'nome_mae',
            # Campos comuns (id_unico é gerado automaticamente)
            'id_projeto', 'projeto_original', 'sexo', 'rg', 'cpf', 'cid10',
            'data_nascimento_mae', 'id_familiar', 'id_lpc_biob',
            # Amostras biológicas
            'amostra_biologica', 'sangue', 'plasma', 'soro', 'pax_gene', 'saliva',
            'scu', 'placenta', 'placenta_ffpe', 'dna', 'rna', 'proteina',
            # Bioinformática
            'metiloma', 'dnam_gene', 'dna_seq', 'exoma', 'rna_seq', 'mi_rna',
            'comprimento_telomerico', 'citocinas', 'cortisol', 'exossomos', 'prs',
            'outros_bioinfo',
            # Dados clínicos
            'historico_materno', 'historico_gravidez', 'historico_familiar',
            'info_parto', 'cars', 'qi', 'comunicacao_vineland', 'hab_dia_vineland',
            'socializacao_vineland', 'adi_total', 'cbcl_internal', 'cbcl_external',
            'score_psiquiatrico_mae', 'score_exposicao_ambiental', 'score_estresse_materno',
            'escolaridade_materna', 'renda_familiar'
        ]
        widgets = {
            'data_nascimento': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'data_nascimento_mae': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'historico_materno': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
            'historico_gravidez': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
            'historico_familiar': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
            'info_parto': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Adiciona classe Bootstrap a todos os campos
        for field_name, field in self.fields.items():
            if not isinstance(field.widget, forms.Textarea):
                if 'class' not in field.widget.attrs:
                    field.widget.attrs['class'] = 'form-control'


class UploadPlanilhaForm(forms.Form):
    """
    Formulário para upload de planilhas Excel ou CSV.
    """
    TIPO_CHOICES = [
        ('amostras', 'Amostras Biológicas'),
        ('bioinformatica', 'Bioinformática'),
        ('dados_clinicos', 'Dados Clínicos'),
        ('auto', 'Detectar Automaticamente'),
    ]
    
    arquivo = forms.FileField(
        label='Arquivo',
        help_text='Selecione um arquivo Excel (.xlsx, .xls) ou CSV (.csv)',
        widget=forms.FileInput(attrs={'class': 'form-control', 'accept': '.xlsx,.xls,.csv'})
    )
    
    tipo_planilha = forms.ChoiceField(
        label='Tipo de Planilha',
        choices=TIPO_CHOICES,
        initial='auto',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    substituir_duplicatas = forms.BooleanField(
        label='Atualizar dados existentes automaticamente',
        required=False,
        initial=False,
        help_text='Se marcado, dados conflitantes serão atualizados sem perguntar. Se desmarcado, você será questionado sobre conflitos.'
    )


class ResolverConflitoForm(forms.Form):
    """
    Formulário para resolver conflitos de dados.
    """
    def __init__(self, *args, conflitos=None, **kwargs):
        super().__init__(*args, **kwargs)
        
        if conflitos:
            for conflito in conflitos:
                field_name = f'conflito_{conflito.id}'
                choices = [
                    ('existente', f'Manter existente: {conflito.valor_existente}'),
                    ('novo', f'Usar novo: {conflito.valor_novo}'),
                ]
                
                self.fields[field_name] = forms.ChoiceField(
                    label=f'{conflito.campo}',
                    choices=choices,
                    widget=forms.RadioSelect(),
                    initial='existente'
                )


class FiltroExportacaoForm(forms.Form):
    """
    Formulário para filtrar dados antes da exportação.
    """
    FORMATO_CHOICES = [
        ('excel', 'Excel (.xlsx)'),
        ('csv', 'CSV (.csv)'),
        ('visualizar', 'Visualizar (imprimir)'),
    ]
    
    # Lista completa de campos disponíveis para exportação
    CAMPOS_DISPONIVEIS = [
        # Dados Principais
        ('nome_paciente', 'Nome do Paciente'),
        ('data_nascimento', 'Data de Nascimento'),
        ('nome_mae', 'Nome da Mãe'),
        
        # Identificação e Projeto
        ('id_projeto', 'ID do Projeto'),
        ('id_unico', 'ID Único'),
        ('projeto_original', 'Projeto Original'),
        ('sexo', 'Sexo'),
        ('rg', 'RG'),
        ('cpf', 'CPF'),
        ('cid10', 'CID10'),
        ('data_nascimento_mae', 'Data de Nascimento da Mãe'),
        ('id_familiar', 'ID Familiar'),
        ('id_lpc_biob', 'ID LPC BIOB'),
        
        # Amostras Biológicas
        ('amostra_biologica', 'Amostra Biológica'),
        ('sangue', 'Sangue'),
        ('plasma', 'Plasma'),
        ('soro', 'Soro'),
        ('pax_gene', 'PaxGene'),
        ('saliva', 'Saliva'),
        ('scu', 'SCU'),
        ('placenta', 'Placenta'),
        ('placenta_ffpe', 'Placenta FFPE'),
        ('dna', 'DNA'),
        ('rna', 'RNA'),
        ('proteina', 'Proteína'),
        
        # Bioinformática
        ('metiloma', 'Metiloma'),
        ('dnam_gene', 'DNAm Gene'),
        ('dna_seq', 'DNA Seq'),
        ('exoma', 'Exoma'),
        ('rna_seq', 'RNA Seq'),
        ('mi_rna', 'miRNA'),
        ('comprimento_telomerico', 'Comprimento Telomérico'),
        ('citocinas', 'Citocinas'),
        ('cortisol', 'Cortisol'),
        ('exossomos', 'Exossomos'),
        ('prs', 'PRS'),
        ('outros_bioinfo', 'Outros (Bioinformática)'),
        
        # Dados Clínicos
        ('historico_materno', 'Histórico Materno'),
        ('historico_gravidez', 'Histórico de Gravidez'),
        ('historico_familiar', 'Histórico Familiar'),
        ('info_parto', 'Informações do Parto'),
        ('cars', 'CARS'),
        ('qi', 'QI'),
        ('comunicacao_vineland', 'Comunicação Vineland'),
        ('hab_dia_vineland', 'Hab. Dia a Dia Vineland'),
        ('socializacao_vineland', 'Socialização Vineland'),
        ('adi_total', 'ADI Total'),
        ('cbcl_internal', 'CBCL Internal'),
        ('cbcl_external', 'CBCL External'),
        ('score_psiquiatrico_mae', 'Score Psiquiátrico Mãe'),
        ('score_exposicao_ambiental', 'Score Exposição Ambiental'),
        ('score_estresse_materno', 'Score Estresse Materno'),
        ('escolaridade_materna', 'Escolaridade Materna'),
        ('renda_familiar', 'Renda Familiar'),
        
        # Metadados
        ('data_cadastro', 'Data de Cadastro'),
        ('data_atualizacao', 'Data de Atualização'),
    ]
    
    formato = forms.ChoiceField(
        label='Formato de Exportação',
        choices=FORMATO_CHOICES,
        widget=forms.RadioSelect(),
        initial='excel'
    )
    
    projeto = forms.CharField(
        label='Filtrar por Projeto (Opcional)',
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control', 
            'placeholder': 'Digite o ID ou nome do projeto'
        })
    )
    
    campos_selecionados = forms.MultipleChoiceField(
        label='Selecione os Campos para Exportar',
        choices=CAMPOS_DISPONIVEIS,
        required=False,
        widget=forms.CheckboxSelectMultiple(),
        help_text='Deixe em branco para exportar TODOS os campos'
    )

