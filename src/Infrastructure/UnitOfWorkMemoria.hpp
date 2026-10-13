#pragma once
#include "../Application/IUnitOfWork.hpp"
#include <iostream>

class UnitOfWorkMemoria : public IUnitOfWork {
public:
    void beginTransaction() override {
        std::cout << "--- [UoW] Inicio de transaccion SQL ---" << std::endl;
    }
    
    void commit() override {
        std::cout << "--- [UoW] Ejecutando COMMIT ---" << std::endl;
    }
    
    void rollback() override {
        std::cout << "--- [UoW] Ejecutando ROLLBACK por fallo ---" << std::endl;
    }
};
