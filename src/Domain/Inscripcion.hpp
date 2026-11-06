#pragma once
#include <string>
#include <stdexcept>
#include <chrono>
#include "Dinero.hpp"

enum class EstadoInscripcion {
    Preinscrita,
    Confirmada,
    CanceladaPorFaltaDePago,
    Completada
};

class Inscripcion {
private:
    std::string id;
    std::string estudianteId;
    std::string grupoId;
    Dinero costoCurso;
    Dinero montoPagado;
    EstadoInscripcion estado;
    std::chrono::system_clock::time_point fechaCreacion;

public:
    Inscripcion(std::string _id, std::string _estudianteId, std::string _grupoId, double _costo);

    std::string getId() const;
    Dinero getSaldoPendiente() const;
    EstadoInscripcion getEstado() const;

    // Reglas de negocio e invariantes encapsuladas
    void confirmarPago(double montoAbonado, int diasTranscurridos);
    void validarEmisionCertificado() const;
};
