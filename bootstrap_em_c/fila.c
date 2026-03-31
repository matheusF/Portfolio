#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <math.h>
#include "fila.h"

Fila* criar_fila(){
    Fila* fila = (Fila*) malloc(sizeof(Fila));
    fila->topo = NULL;
    return fila;
}

void enfileirar(Fila* fila, double valor){
    if(fila->topo == NULL){
        fila->topo = (No*) malloc(sizeof(No));
        fila->topo->valor = valor;
        fila->topo->proximo = NULL;
    }else if(fila->topo != NULL){
        No* no_atual = fila->topo;
        while(no_atual->proximo != NULL){
            no_atual = no_atual->proximo;
        }
        no_atual->proximo = (No*) malloc(sizeof(No));
        no_atual->proximo->valor = valor;
        no_atual->proximo->proximo = NULL;
    }
}

double desenfileirar(Fila* fila){
    double valor_retornado = fila->topo->valor;
    No* topo_antigo = fila->topo;
    fila->topo = fila->topo->proximo;
    free(topo_antigo);
    return valor_retornado;
}

int tamanho_fila(Fila* fila){
    int i = 1;
    if(fila->topo == NULL){
        return 0;
    } else if(fila->topo != NULL){
        No* no_atual = fila->topo;
        while(no_atual->proximo != NULL){
            i++;
            no_atual = no_atual->proximo;
        }
    }
    return i;
}

double* fila_para_array(Fila* fila){
    int n = tamanho_fila(fila);
    double* arr = (double*) malloc(n * sizeof(double));
    for(int i = 0; i < n; i++){
        arr[i] = desenfileirar(fila);
    }
    return arr;
}
