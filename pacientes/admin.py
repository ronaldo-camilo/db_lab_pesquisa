from django.contrib import admin
from .models import Paciente, ConflitoDados


@admin.register(Paciente)
class PacienteAdmin(admin.ModelAdmin):
    list_display = [
        'nome_paciente',
        'data_nascimento',
        'sexo',
        'id_projeto',
        'fonte_dados',
        'data_cadastro'
    ]
    list_filter = ['sexo', 'fonte_dados', 'data_cadastro']
    search_fields = ['nome_paciente', 'nome_mae', 'cpf', 'id_projeto']
    date_hierarchy = 'data_cadastro'
    
    fieldsets = (
        ('Dados Principais', {
            'fields': ('nome_paciente', 'data_nascimento', 'nome_mae')
        }),
        ('Identificação', {
            'fields': ('id_projeto', 'id_unico', 'projeto_original', 'sexo', 'rg', 'cpf', 'cid10')
        }),
        ('Informações Familiares', {
            'fields': ('data_nascimento_mae', 'id_familiar', 'id_lpc_biob'),
            'classes': ('collapse',)
        }),
        ('Amostras Biológicas', {
            'fields': (
                'amostra_biologica', 'sangue', 'plasma', 'soro', 'pax_gene',
                'saliva', 'scu', 'placenta', 'placenta_ffpe', 'dna', 'rna', 'proteina'
            ),
            'classes': ('collapse',)
        }),
        ('Bioinformática', {
            'fields': (
                'metiloma', 'dnam_gene', 'dna_seq', 'exoma', 'rna_seq', 'mi_rna',
                'comprimento_telomerico', 'citocinas', 'cortisol', 'exossomos',
                'prs', 'outros_bioinfo'
            ),
            'classes': ('collapse',)
        }),
        ('Dados Clínicos', {
            'fields': (
                'historico_materno', 'historico_gravidez', 'historico_familiar',
                'info_parto', 'cars', 'qi', 'comunicacao_vineland', 'hab_dia_vineland',
                'socializacao_vineland', 'adi_total', 'cbcl_internal', 'cbcl_external',
                'score_psiquiatrico_mae', 'score_exposicao_ambiental',
                'score_estresse_materno', 'escolaridade_materna', 'renda_familiar'
            ),
            'classes': ('collapse',)
        }),
        ('Metadados', {
            'fields': ('fonte_dados', 'data_cadastro', 'data_atualizacao'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['data_cadastro', 'data_atualizacao']


@admin.register(ConflitoDados)
class ConflitoDadosAdmin(admin.ModelAdmin):
    list_display = [
        'paciente',
        'campo',
        'valor_existente',
        'valor_novo',
        'status',
        'data_conflito'
    ]
    list_filter = ['status', 'campo', 'data_conflito']
    search_fields = ['paciente__nome_paciente', 'campo']
    date_hierarchy = 'data_conflito'
    
    fieldsets = (
        ('Informações do Conflito', {
            'fields': ('paciente', 'campo', 'valor_existente', 'valor_novo')
        }),
        ('Resolução', {
            'fields': ('status', 'valor_escolhido', 'resolvido_por', 'data_resolucao')
        }),
    )
    
    readonly_fields = ['data_conflito']
