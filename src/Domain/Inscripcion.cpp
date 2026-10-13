#include "Inscripcion.hpp"

Inscripcion::Inscripcion(std::string _id, std::string _estudianteId, std::string _grupoId, double _costo)
    : id(_id), estudianteId(_estudianteId), grupoId(_grupoId), costoCurso(_costo), montoPagado(0.0),
      estado(EstadoInscripcion::Preinscrita), fechaCreacion(std::chrono::system_clock::now()) {}

std::string Inscripcion::getId() const { return id; }

Dinero Inscripcion::getSaldoPendiente() const {
    return Dinero(costoCurso.monto - montoPagado.monto);
}

EstadoInscripcion Inscripcion::getEstado() const { return estado; }

void Inscripcion::confirmarPago(double montoAbonado, int diasTranscurridos) {
    // Regla: Plazo máximo de 3 días hábiles (RN-17)
    if (diasTranscurridos > 3) {
        estado = EstadoInscripcion::CanceladaPorFaltaDePago;
        throw std::runtime_error("El plazo de 3 dias habiles ha vencido. Cupo liberado.");
    }

    montoPagado.monto += montoAbonado;

    // Regla: Anticipo mínimo del 50% (RN-01)
    if (montoPagado >= costoCurso * 0.50) {
        estado = EstadoInscripcion::Confirmada;
    } else {
        throw std::runtime_error("El anticipo es menor al 50% requerido.");
    }
}

void Inscripcion::validarEmisionCertificado() const {
    // Invariante financiero absoluto: Saldo pendiente debe ser 0 (RN-22)
    if (getSaldoPendiente().monto > 0) {
        throw std::runtime_error("Emision bloqueada: El estudiante mantiene saldo pendiente de pago.");
    }
}
