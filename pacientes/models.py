from django.db import models
from django.core.exceptions import ValidationError


class Paciente(models.Model):
    """
    Modelo unificado que combina dados de:
    - Amostras Biológicas
    - Bioinformática
    - Dados Clínicos
    
    Campos principais para identificação de duplicatas:
    - nome_paciente
    - data_nascimento
    - nome_mae
    """
    
    # ===== CAMPOS PRINCIPAIS (Chaves de Identificação) =====
    nome_paciente = models.CharField(
        max_length=255,
        verbose_name="Nome do Paciente",
        help_text="Campo obrigatório para identificação"
    )
    data_nascimento = models.DateField(
        verbose_name="Data de Nascimento",
        help_text="Campo obrigatório para identificação"
    )
    nome_mae = models.CharField(
        max_length=255,
        verbose_name="Nome da Mãe",
        help_text="Campo obrigatório para identificação"
    )
    
    # ===== CAMPOS COMUNS =====
    id_projeto = models.CharField(max_length=100, null=True, blank=True, verbose_name="ID do Projeto")
    id_unico = models.CharField(max_length=100, null=True, blank=True, unique=True, editable=False, verbose_name="ID Único")
    projeto_original = models.CharField(max_length=255, null=True, blank=True, verbose_name="Projeto Original")
    sexo = models.CharField(max_length=50, null=True, blank=True, verbose_name="Sexo")
    rg = models.CharField(max_length=50, null=True, blank=True, verbose_name="RG")
    cpf = models.CharField(max_length=14, null=True, blank=True, verbose_name="CPF")
    cid10 = models.CharField(max_length=10, null=True, blank=True, verbose_name="CID10")
    data_nascimento_mae = models.DateField(null=True, blank=True, verbose_name="Data de Nascimento da Mãe")
    id_familiar = models.CharField(max_length=100, null=True, blank=True, verbose_name="ID Familiar")
    id_lpc_biob = models.CharField(max_length=100, null=True, blank=True, verbose_name="ID LPC BIOB")
    
    # ===== AMOSTRAS BIOLÓGICAS =====
    amostra_biologica = models.CharField(max_length=255, null=True, blank=True, verbose_name="Amostra Biológica")
    sangue = models.CharField(max_length=50, null=True, blank=True, verbose_name="Sangue")
    plasma = models.CharField(max_length=50, null=True, blank=True, verbose_name="Plasma")
    soro = models.CharField(max_length=50, null=True, blank=True, verbose_name="Soro")
    pax_gene = models.CharField(max_length=50, null=True, blank=True, verbose_name="PaxGene")
    saliva = models.CharField(max_length=50, null=True, blank=True, verbose_name="Saliva")
    scu = models.CharField(max_length=50, null=True, blank=True, verbose_name="SCU")
    placenta = models.CharField(max_length=50, null=True, blank=True, verbose_name="Placenta")
    placenta_ffpe = models.CharField(max_length=50, null=True, blank=True, verbose_name="Placenta FFPE")
    dna = models.CharField(max_length=50, null=True, blank=True, verbose_name="DNA")
    rna = models.CharField(max_length=50, null=True, blank=True, verbose_name="RNA")
    proteina = models.CharField(max_length=50, null=True, blank=True, verbose_name="Proteína")
    
    # ===== BIOINFORMÁTICA =====
    metiloma = models.CharField(max_length=50, null=True, blank=True, verbose_name="Metiloma")
    dnam_gene = models.CharField(max_length=50, null=True, blank=True, verbose_name="DNAm Gene")
    dna_seq = models.CharField(max_length=50, null=True, blank=True, verbose_name="DNA Seq")
    exoma = models.CharField(max_length=50, null=True, blank=True, verbose_name="Exoma")
    rna_seq = models.CharField(max_length=50, null=True, blank=True, verbose_name="RNA Seq")
    mi_rna = models.CharField(max_length=50, null=True, blank=True, verbose_name="miRNA")
    comprimento_telomerico = models.CharField(max_length=50, null=True, blank=True, verbose_name="Comprimento Telomérico")
    citocinas = models.CharField(max_length=50, null=True, blank=True, verbose_name="Citocinas")
    cortisol = models.CharField(max_length=50, null=True, blank=True, verbose_name="Cortisol")
    exossomos = models.CharField(max_length=50, null=True, blank=True, verbose_name="Exossomos")
    prs = models.CharField(max_length=50, null=True, blank=True, verbose_name="PRS")
    outros_bioinfo = models.CharField(max_length=255, null=True, blank=True, verbose_name="Outros (Bioinformática)")
    
    # ===== DADOS CLÍNICOS =====
    historico_materno = models.TextField(null=True, blank=True, verbose_name="Histórico Materno")
    historico_gravidez = models.TextField(null=True, blank=True, verbose_name="Histórico de Gravidez")
    historico_familiar = models.TextField(null=True, blank=True, verbose_name="Histórico Familiar")
    info_parto = models.TextField(null=True, blank=True, verbose_name="Informações do Parto")
    cars = models.CharField(max_length=100, null=True, blank=True, verbose_name="CARS")
    qi = models.CharField(max_length=100, null=True, blank=True, verbose_name="QI")
    comunicacao_vineland = models.CharField(max_length=100, null=True, blank=True, verbose_name="Comunicação Vineland")
    hab_dia_vineland = models.CharField(max_length=100, null=True, blank=True, verbose_name="Hab. Dia a Dia Vineland")
    socializacao_vineland = models.CharField(max_length=100, null=True, blank=True, verbose_name="Socialização Vineland")
    adi_total = models.CharField(max_length=100, null=True, blank=True, verbose_name="ADI Total")
    cbcl_internal = models.CharField(max_length=100, null=True, blank=True, verbose_name="CBCL Internal")
    cbcl_external = models.CharField(max_length=100, null=True, blank=True, verbose_name="CBCL External")
    score_psiquiatrico_mae = models.CharField(max_length=100, null=True, blank=True, verbose_name="Score Psiquiátrico Mãe")
    score_exposicao_ambiental = models.CharField(max_length=100, null=True, blank=True, verbose_name="Score Exposição Ambiental na Gestação")
    score_estresse_materno = models.CharField(max_length=100, null=True, blank=True, verbose_name="Score Estresse Materno")
    escolaridade_materna = models.CharField(max_length=100, null=True, blank=True, verbose_name="Escolaridade Materna")
    renda_familiar = models.CharField(max_length=100, null=True, blank=True, verbose_name="Renda Familiar")
    
    # ===== METADADOS =====
    data_cadastro = models.DateTimeField(auto_now_add=True, verbose_name="Data de Cadastro")
    data_atualizacao = models.DateTimeField(auto_now=True, verbose_name="Data de Atualização")
    
    class Meta:
        verbose_name = "Paciente"
        verbose_name_plural = "Pacientes"
        ordering = ['-data_cadastro']
        indexes = [
            models.Index(fields=['nome_paciente', 'data_nascimento', 'nome_mae']),
        ]
    
    def __str__(self):
        return f"{self.nome_paciente} - {self.data_nascimento}"
    
    def save(self, *args, **kwargs):
        """
        Gera ID_unico automaticamente se não existir.
        Formato: PSB_UnXXXX onde XXXX é o ID do registro.
        """
        if not self.id_unico:
            # Primeiro, salva para obter o ID
            super().save(*args, **kwargs)
            # Depois, gera o ID_unico baseado no ID do registro
            self.id_unico = f"PSB_Un{self.id}"
            # Salva novamente com o ID_unico
            super().save(update_fields=['id_unico'])
        else:
            super().save(*args, **kwargs)
    
    @classmethod
    def buscar_duplicata(cls, nome_paciente, data_nascimento, nome_mae):
        """
        Busca pacientes duplicados com base em Nome + Data de Nascimento.
        Nome da mãe é verificado como campo de conflito se divergir.
        Retorna o paciente encontrado ou None.
        """
        try:
            return cls.objects.get(
                nome_paciente__iexact=nome_paciente,
                data_nascimento=data_nascimento
            )
        except cls.DoesNotExist:
            return None
        except cls.MultipleObjectsReturned:
            # Se houver múltiplos, retorna o primeiro
            return cls.objects.filter(
                nome_paciente__iexact=nome_paciente,
                data_nascimento=data_nascimento,
                nome_mae__iexact=nome_mae
            ).first()


class ConflitoDados(models.Model):
    """
    Armazena conflitos de dados que precisam de resolução manual.
    """
    TIPO_CHOICES = [
        ('novo', 'Novo Conflito'),
        ('resolvido', 'Resolvido'),
        ('ignorado', 'Ignorado'),
    ]
    
    paciente = models.ForeignKey(
        Paciente,
        on_delete=models.CASCADE,
        related_name='conflitos',
        verbose_name="Paciente"
    )
    campo = models.CharField(max_length=100, verbose_name="Campo em Conflito")
    valor_existente = models.TextField(verbose_name="Valor Existente no Banco")
    valor_novo = models.TextField(verbose_name="Valor Novo a Ser Inserido")
    status = models.CharField(
        max_length=20,
        choices=TIPO_CHOICES,
        default='novo',
        verbose_name="Status"
    )
    valor_escolhido = models.TextField(
        null=True,
        blank=True,
        verbose_name="Valor Escolhido"
    )
    data_conflito = models.DateTimeField(auto_now_add=True, verbose_name="Data do Conflito")
    data_resolucao = models.DateTimeField(null=True, blank=True, verbose_name="Data de Resolução")
    resolvido_por = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name="Resolvido Por"
    )
    
    class Meta:
        verbose_name = "Conflito de Dados"
        verbose_name_plural = "Conflitos de Dados"
        ordering = ['-data_conflito']
    
    def __str__(self):
        return f"Conflito: {self.paciente.nome_paciente} - {self.campo}"
