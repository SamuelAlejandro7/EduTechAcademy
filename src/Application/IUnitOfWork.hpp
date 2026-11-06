#pragma once

class IUnitOfWork {
public:
    virtual ~IUnitOfWork() = default;
    virtual void beginTransaction() = 0;
    virtual void commit() = 0;
    virtual void rollback() = 0;
};
