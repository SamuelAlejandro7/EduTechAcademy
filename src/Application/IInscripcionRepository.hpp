#pragma once
#include <memory>
#include <string>
#include "../Domain/Inscripcion.hpp"

class IInscripcionRepository {
public:
    virtual ~IInscripcionRepository() = default;
    virtual std::shared_ptr<Inscripcion> obtenerPorId(const std::string& id) = 0;
    virtual void guardar(std::shared_ptr<Inscripcion> inscripcion) = 0;
};
