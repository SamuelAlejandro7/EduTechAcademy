#pragma once
#include <memory>
#include <stdexcept>
#include <iostream>
#include "IInscripcionRepository.hpp"
#include "IUnitOfWork.hpp"

// DTO / Comando de entrada
struct ConfirmarPagoCommand {
    std::string inscripcionId;
    double monto;
    int diasTranscurridos;
};

class InscripcionApplicationService {
private:
    std::shared_ptr<IInscripcionRepository> inscripcionRepository;
    std::shared_ptr<IUnitOfWork> unitOfWork;

public:
    InscripcionApplicationService(
        std::shared_ptr<IInscripcionRepository> _repo, 
        std::shared_ptr<IUnitOfWork> _uow) 
        : inscripcionRepository(_repo), unitOfWork(_uow) {}

    void confirmarInscripcion(const ConfirmarPagoCommand& command) {
        unitOfWork->beginTransaction();

        try {
            auto inscripcion = inscripcionRepository->obtenerPorId(command.inscripcionId);
            
            if (!inscripcion) {
                throw std::runtime_error("Inscripcion no encontrada.");
            }

            inscripcion->confirmarPago(command.monto, command.diasTranscurridos);
            inscripcionRepository->guardar(inscripcion);

            unitOfWork->commit();
            std::cout << "[AppService] Transaccion de confirmacion completada con exito.\n" << std::endl;
        } 
        catch (const std::exception& e) {
            unitOfWork->rollback();
            std::cerr << "[AppService] Error capturado. Rollback ejecutado: " << e.what() << "\n" << std::endl;
            throw;
        }
    }
};
