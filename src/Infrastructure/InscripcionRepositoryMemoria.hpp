#pragma once
#include "../Application/IInscripcionRepository.hpp"
#include <iostream>

class InscripcionRepositoryMemoria : public IInscripcionRepository {
public:
    std::shared_ptr<Inscripcion> obtenerPorId(const std::string& id) override {
        // Simulando recuperación y creación de la entidad con un costo de curso de $1000.0
        return std::make_shared<Inscripcion>(id, "EST-001", "GRU-101", 1000.0);
    }
    
    void guardar(std::shared_ptr<Inscripcion> inscripcion) override {
        std::cout << " -> [Infraestructura] Estado de la inscripcion " << inscripcion->getId() 
                  << " actualizado en base de datos relacional." << std::endl;
    }
};
