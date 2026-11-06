#pragma once

struct Dinero {
    double monto;
    Dinero(double m = 0.0) : monto(m) {}

    Dinero operator+(const Dinero& otro) const { return Dinero(monto + otro.monto); }
    Dinero operator-(const Dinero& otro) const { return Dinero(monto - otro.monto); }
    Dinero operator*(double factor) const { return Dinero(monto * factor); }
    bool operator>=(const Dinero& otro) const { return monto >= otro.monto; }
};
