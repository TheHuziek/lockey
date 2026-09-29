from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker

# Configura tu conexión a MariaDB (usuario:password@host:puerto/nombre_bd)
DATABASE_URL = "mysql+pymysql://usuario:password@localhost:3306/mi_base_de_datos"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class UsuarioModel(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nombre = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)

# Crea las tablas en MariaDB si no existen
def init_db():
    Base.metadata.create_all(bind=engine)