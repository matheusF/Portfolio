#ifndef FILA_H
#define FILA_H

typedef struct No {
    double valor;
    struct No *proximo;
} No;

typedef struct Fila {
    No *topo;
} Fila;

Fila* criar_fila();
void enfileirar(Fila* fila, double valor);
double desenfileirar(Fila* fila);
int tamanho_fila(Fila* fila);
double* fila_para_array(Fila* fila);

#endif // FILA_H_INCLUDED
