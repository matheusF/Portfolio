#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <math.h>
#include "fila.h"
#define PI 3.14159265

typedef struct Array {
    double* arr;
    int n;
} Array;

Array* criar_array(int n){
    Array* array = (Array*) malloc(sizeof(Array));
    array->arr = (double*) malloc(n * sizeof(double));
    array->n = n;
    return array;
}

void liberar_array(Array* array){
    free(array->arr);
    free(array);
}

int* gerar_aleatorio_ate_n(int n){
    // srand(time(NULL));
    int aleatorio;
    int *numeros_aleatorios = (int*) malloc(n * sizeof(int));
    for(int i = 0; i < n; i++){
        aleatorio = (int) rand() % n;
        numeros_aleatorios[i] = aleatorio;
    }
    return numeros_aleatorios;
}

Array* ler_lista_numeros(){
    FILE *p_file;
    p_file = fopen("dados.txt", "r");
    char var_string[1000];
    Fila* fila = criar_fila();
    int i = 0;
    while(fgets(var_string, 1000, p_file)){
        enfileirar(fila, atof(var_string));
        i++;
    }
    Array* array = (Array*) malloc(i * sizeof(Array));
    array->arr = fila_para_array(fila);
    free(fila);
    array->n = i;
    return array;
}

Array* gerar_reamostra(Array* array){ // ideia de nome: obter_amostra_bootstrap ou gerar_reamostra
    int *numeros_aleatorios = gerar_aleatorio_ate_n(array->n);
    Array* resultado = criar_array(array->n);
    for(int i = 0; i < array->n; i++){
        resultado->arr[i] = array->arr[numeros_aleatorios[i]];
    }
    free(numeros_aleatorios);
    return resultado;
}

double soma(Array* array){
    double soma = 0;
    for(int i = 0; i < array->n; i++){
        soma += array->arr[i];
    }
    return soma;
}

double estatistica(Array* array){
    double resultado = 0;
    resultado = soma(array)/array->n;
    return resultado;
}

double media(Array* array){
    double resultado = 0;
    resultado = soma(array)/array->n;
    return resultado;
}

double* retornar_amostra_bootstrap(Array* array, int B){ // incluir estatística no cabeçalho da função
    double* amostra_bootstrap = (double*) malloc(B * sizeof(double));
    Array* reamostra;// = (Array*) malloc(sizeof(Array));
    for(int i = 0; i < B; i++){
        reamostra = gerar_reamostra(array);
        amostra_bootstrap[i] = estatistica(reamostra);
        liberar_array(reamostra);
    }
    return amostra_bootstrap;
}

double calcular_a(Array* array){ // incluir estatística no cabeçalho da função
    Array* amostra_sem_i = criar_array(array->n - 1);
    Array* estimador_sem_amostra_i = criar_array(array->n);
    for(int i = 0; i < array->n; i++){
        for(int j = 0; j < array->n-1; j++){
            if(j < i){
                amostra_sem_i->arr[j] = array->arr[j];
            }
            if(j >= i){
                amostra_sem_i->arr[j] = array->arr[j+1];
            }
        }
        estimador_sem_amostra_i->arr[i] = estatistica(amostra_sem_i);
    }
    double media_dos_estimadores_sem_i = media(estimador_sem_amostra_i);
    double numerador = 0.0, denominador = 0.0;
    for(int i = 0; i < array->n; i++){
        numerador += pow(media_dos_estimadores_sem_i - estimador_sem_amostra_i->arr[i], 3);
        denominador += pow(media_dos_estimadores_sem_i - estimador_sem_amostra_i->arr[i], 2);
    }
    denominador = pow(denominador, 3.0/2.0)*6;
    liberar_array(amostra_sem_i);
    liberar_array(estimador_sem_amostra_i);
    return numerador/denominador;
}

double normal_acumulada(double valor){
    double resultado = (1 + erf(valor/sqrt(2)))/2.0;
    return resultado;
}

double g(double x, double valor){
    return 1.0/2*(1 + erf(x/sqrt(2))) - valor;
}

double gl(double x){ // derivada de g
    return -2/sqrt(2*PI)*exp(-x*x/2);
}

double normal_acumulada_inversa(double valor, double erro_minimo){
    double x = 0.1, x_anterior = 0.9, aux;
    while(fabs(x - x_anterior) > erro_minimo){
        aux = x;
        x = x - g(x, valor)*(x - x_anterior)/(g(x, valor) - g(x_anterior, valor));
        x_anterior = aux;
    }
    return x;
}

double calcular_z0(Array* array, double* amostra_bootstrap, int B){
    double _media = media(array);
    double contador = 0.0;
    for(int i = 0; i < B; i++){
        if(amostra_bootstrap[i] < _media){
            contador += 1.0;
        }
    }
    double z0 = normal_acumulada_inversa(contador/B, 0.0001);
    return z0;
}

int funcao_comparadora_qsort(const void *a, const void *b){
    double valor_a = *(double*) a;
    double valor_b = *(double*) b;
    if(valor_a > valor_b){
        return 1;
    }
    if(valor_a < valor_b){
        return -1;
    }
    return 0;
}

double quantil(double* arr, int tamanho_array, double q){
    qsort(arr, tamanho_array, sizeof(double), funcao_comparadora_qsort);
    double posicao_incerta = q*(tamanho_array+1);
    int posicao_truncada = trunc(posicao_incerta);
    double parte_decimal = posicao_incerta - posicao_truncada;
    double resultado = arr[posicao_truncada-1] + parte_decimal*(arr[posicao_truncada] - arr[posicao_truncada-1]);
    return resultado;
}

double* intervalo_confianca(Array* array, int B, double nivel_descritivo){
    double* amostra_bootstrap = malloc(B * sizeof(double));
    amostra_bootstrap = retornar_amostra_bootstrap(array, B);
    double ALFA = nivel_descritivo;
    double z0 = calcular_z0(array, amostra_bootstrap, B);
    double a = calcular_a(array);
    double alfa1 = normal_acumulada(z0 + (z0 + normal_acumulada_inversa(ALFA/2, 0.0001))/(1 - a*(z0 + normal_acumulada_inversa(ALFA/2, 0.0001))));
    double alfa2 = normal_acumulada(z0 + (z0 + normal_acumulada_inversa(1 - ALFA/2, 0.0001))/(1 - a*(z0 + normal_acumulada_inversa(1 - ALFA/2, 0.0001))));
    double* intervalo_confianca = (double*) malloc(2 * sizeof(double));
    intervalo_confianca[0] = quantil(amostra_bootstrap, B, alfa1);
    intervalo_confianca[1] = quantil(amostra_bootstrap, B, alfa2);
    free(amostra_bootstrap);
    return intervalo_confianca;
}

int main(){
    time_t tempo_inicial = clock();

    srand(time(NULL));
    
    Array* array = ler_lista_numeros();
    double* intervalo = intervalo_confianca(array, 1000000, 0.05);
    liberar_array(array);
    printf("invervalo de confianca: [%f, %f]\n", intervalo[0], intervalo[1]);

    printf("Tempo de execucao: %f\n", (double) (clock() - tempo_inicial)/CLOCKS_PER_SEC);

    // system("pause");
    
    return 0;
}
