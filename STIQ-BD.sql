-- Adminer 4.8.1 MySQL 8.0.3-rc-log dump

SET NAMES utf8;
SET time_zone = '+00:00';
SET foreign_key_checks = 0;

DROP TABLE IF EXISTS `Equipo`;
CREATE TABLE `Equipo` (
  `idEquipo` int(11) NOT NULL AUTO_INCREMENT,
  `Nombre` varchar(80) NOT NULL,
  PRIMARY KEY (`idEquipo`)
) ENGINE=InnoDB AUTO_INCREMENT=14 DEFAULT CHARSET=latin1;


DELIMITER ;;

CREATE TRIGGER `trg_equipo_insert` AFTER INSERT ON `Equipo` FOR EACH ROW
BEGIN
  INSERT INTO Historial_Equipos (
    idEquipo,
    fechaCambio,
    idUsuario,
    tipoOperacion,
    observaciones
  ) VALUES (
    NEW.idEquipo,
    NOW(),
    @idUsuario,
    'INSERT',
    'Nuevo equipo creado'
  );
END;;

CREATE TRIGGER `trg_equipo_update` AFTER UPDATE ON `Equipo` FOR EACH ROW
BEGIN
  IF OLD.Nombre <> NEW.Nombre THEN
    INSERT INTO Historial_Equipos (
      idEquipo,
      fechaCambio,
      idUsuario,
      tipoOperacion,
      campo,
      valorAnterior,
      valorNuevo,
      observaciones
    ) VALUES (
      NEW.idEquipo,
      NOW(),
      @idUsuario,
      'UPDATE',
      'Nombre',
      OLD.Nombre,
      NEW.Nombre,
      CONCAT('Cambio de nombre: ', OLD.Nombre, ' -> ', NEW.Nombre)
    );
  END IF;
END;;

CREATE TRIGGER `trg_equipo_delete` AFTER DELETE ON `Equipo` FOR EACH ROW
BEGIN
  INSERT INTO Historial_Equipos (
    idEquipo,
    fechaCambio,
    idUsuario,
    tipoOperacion,
    observaciones
  ) VALUES (
    OLD.idEquipo,
    NOW(),
    @idUsuario,
    'DELETE',
    'Equipo eliminado'
  );
END;;

DELIMITER ;

DROP TABLE IF EXISTS `Equipo_Instrumento`;
CREATE TABLE `Equipo_Instrumento` (
  `idEquipo` int(11) NOT NULL,
  `idInstrumento` int(11) NOT NULL,
  `cantidad` int(11) NOT NULL,
  PRIMARY KEY (`idEquipo`,`idInstrumento`),
  KEY `FK_EquipoGInstrumento_GInstrumento` (`idInstrumento`),
  CONSTRAINT `FK_EquipoGInstrumento_Equipo` FOREIGN KEY (`idEquipo`) REFERENCES `Equipo` (`idequipo`),
  CONSTRAINT `FK_EquipoGInstrumento_GInstrumento` FOREIGN KEY (`idInstrumento`) REFERENCES `GInstrumento` (`idinstrumento`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;


DELIMITER ;;

CREATE TRIGGER `trg_equipo_instrumento_insert` AFTER INSERT ON `Equipo_Instrumento` FOR EACH ROW
BEGIN
  INSERT INTO Historial_Equipos (
    idEquipo,
    idInstrumento,
    fechaCambio,
    idUsuario,
    tipoOperacion,
    observaciones
  ) VALUES (
    NEW.idEquipo,
    NEW.idInstrumento,
    NOW(),
    @idUsuario,
    'INSERT',
    'Instrumento agregado al equipo'
  );
END;;

CREATE TRIGGER `trg_equipo_instrumento_update` AFTER UPDATE ON `Equipo_Instrumento` FOR EACH ROW
BEGIN
  IF OLD.cantidad <> NEW.cantidad THEN
    INSERT INTO Historial_Equipos (
      idEquipo,
      idInstrumento,
      fechaCambio,
      idUsuario,
      tipoOperacion,
      campo,
      valorAnterior,
      valorNuevo,
      observaciones
    ) VALUES (
      NEW.idEquipo,
      NEW.idInstrumento,
      NOW(),
      @idUsuario,
      'UPDATE',
      'cantidad',
      OLD.cantidad,
      NEW.cantidad,
      CONCAT('Cantidad modificada: ', OLD.cantidad, ' -> ', NEW.cantidad)
    );
  END IF;
END;;

CREATE TRIGGER `trg_equipo_instrumento_delete` AFTER DELETE ON `Equipo_Instrumento` FOR EACH ROW
BEGIN
  INSERT INTO Historial_Equipos (
    idEquipo,
    idInstrumento,
    fechaCambio,
    idUsuario,
    tipoOperacion,
    observaciones
  ) VALUES (
    OLD.idEquipo,
    OLD.idInstrumento,
    NOW(),
    @idUsuario,
    'DELETE',
    'Instrumento removido del equipo'
  );
END;;

DELIMITER ;

DROP TABLE IF EXISTS `Especialidad`;
CREATE TABLE `Especialidad` (
  `idEspecialidad` int(11) NOT NULL AUTO_INCREMENT,
  `Nombre` varchar(45) NOT NULL,
  PRIMARY KEY (`idEspecialidad`)
) ENGINE=InnoDB AUTO_INCREMENT=16 DEFAULT CHARSET=utf8;


DROP TABLE IF EXISTS `GInstrumento`;
CREATE TABLE `GInstrumento` (
  `idInstrumento` int(11) NOT NULL AUTO_INCREMENT,
  `CodigoDeBarras` varchar(15) NOT NULL,
  `Cantidad` int(11) NOT NULL,
  `Nombre` varchar(80) NOT NULL,
  PRIMARY KEY (`idInstrumento`)
) ENGINE=InnoDB AUTO_INCREMENT=27 DEFAULT CHARSET=latin1 COMMENT='Objeto de Instrumentos como Grupo';


DELIMITER ;;

CREATE TRIGGER `trg_Ginstrumento_insert` AFTER INSERT ON `GInstrumento` FOR EACH ROW
BEGIN
  INSERT INTO Historial_GInstrumento (
    idInstrumento,
    fechaCambio,
    idUsuario,
    observaciones
  )
  VALUES (
    NEW.idInstrumento,
    NOW(),
    @idUsuario,
    'INSERT'
  );
END;;

CREATE TRIGGER `trg_Ginstrumento_update` AFTER UPDATE ON `GInstrumento` FOR EACH ROW
BEGIN
  DECLARE cambio TEXT DEFAULT '';

  IF OLD.Nombre <> NEW.Nombre THEN
    SET cambio = CONCAT(cambio, 'UPDATE: Nombre ', OLD.Nombre, '->', NEW.Nombre, '
');
  END IF;

  IF OLD.CodigoDeBarras <> NEW.CodigoDeBarras THEN
    SET cambio = CONCAT(cambio, 'UPDATE: CodigoDeBarras ', OLD.CodigoDeBarras, '->', NEW.CodigoDeBarras, '
');
  END IF;

  IF OLD.Cantidad <> NEW.Cantidad THEN
    SET cambio = CONCAT(cambio, 'UPDATE: Cantidad ', OLD.Cantidad, '->', NEW.Cantidad, '
');
  END IF;

  IF cambio <> '' THEN
    INSERT INTO Historial_GInstrumento (
      idInstrumento,
      fechaCambio,
      idUsuario,
      observaciones
    )
    VALUES (
      NEW.idInstrumento,
      NOW(),
      @idUsuario,
      cambio
    );
  END IF;
END;;

CREATE TRIGGER `trg_Ginstrumento_delete` AFTER DELETE ON `GInstrumento` FOR EACH ROW
BEGIN
  INSERT INTO Historial_GInstrumento (
    idInstrumento,
    fechaCambio,
    idUsuario,
    observaciones
  )
  VALUES (
    OLD.idInstrumento,
    NOW(),
    @idUsuario,
    'DELETE'
  );
END;;

DELIMITER ;

DROP TABLE IF EXISTS `Historial_Equipos`;
CREATE TABLE `Historial_Equipos` (
  `idHistorialEquipo` int(11) NOT NULL AUTO_INCREMENT,
  `idEquipo` int(11) NOT NULL,
  `idInstrumento` int(11) DEFAULT NULL,
  `fechaCambio` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `idUsuario` int(11) DEFAULT NULL,
  `tipoOperacion` enum('INSERT','UPDATE','DELETE') NOT NULL,
  `campo` varchar(80) DEFAULT NULL,
  `valorAnterior` text,
  `valorNuevo` text,
  `observaciones` text,
  `nombreEquipoPrevio` varchar(255) NOT NULL DEFAULT '',
  PRIMARY KEY (`idHistorialEquipo`),
  KEY `fk_historial_equipo_usuario` (`idUsuario`)
) ENGINE=MyISAM AUTO_INCREMENT=56 DEFAULT CHARSET=latin1;


DROP TABLE IF EXISTS `Historial_GInstrumento`;
CREATE TABLE `Historial_GInstrumento` (
  `idHistorial` int(11) NOT NULL AUTO_INCREMENT,
  `idInstrumento` int(11) NOT NULL,
  `fechaCambio` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `idUsuario` int(11) DEFAULT NULL,
  `observaciones` text,
  `nombreInstrumentoPrevio` varchar(255) NOT NULL DEFAULT '',
  PRIMARY KEY (`idHistorial`),
  KEY `FK_Historial_Usuario` (`idUsuario`),
  CONSTRAINT `FK_Historial_Usuario` FOREIGN KEY (`idUsuario`) REFERENCES `Usuario` (`idusuario`)
) ENGINE=InnoDB AUTO_INCREMENT=63 DEFAULT CHARSET=latin1;


DROP TABLE IF EXISTS `Historial_IInstrumento`;
CREATE TABLE `Historial_IInstrumento` (
  `idHistorialIndividual` int(11) NOT NULL AUTO_INCREMENT,
  `idInstrumentoIndividual` int(11) NOT NULL,
  `fechaCambio` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `idUsuario` int(11) DEFAULT NULL,
  `observaciones` text,
  `nombreHerramientaPrevio` varchar(255) NOT NULL DEFAULT '',
  PRIMARY KEY (`idHistorialIndividual`),
  KEY `fk_iinstrumento_usuario` (`idUsuario`)
) ENGINE=MyISAM AUTO_INCREMENT=300 DEFAULT CHARSET=latin1;


DROP TABLE IF EXISTS `Historial_Paquetes`;
CREATE TABLE `Historial_Paquetes` (
  `idHistorialPaquete` int(11) NOT NULL AUTO_INCREMENT,
  `idPaquete` int(11) NOT NULL,
  `idEquipo` int(11) DEFAULT NULL,
  `idInstrumento` int(11) DEFAULT NULL,
  `fechaCambio` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `idUsuario` int(11) DEFAULT NULL,
  `tipoOperacion` enum('INSERT','UPDATE','DELETE') NOT NULL,
  `campo` varchar(80) DEFAULT NULL,
  `valorAnterior` text,
  `valorNuevo` text,
  `observaciones` text,
  `nombrePaquetePrevio` varchar(255) NOT NULL DEFAULT '',
  PRIMARY KEY (`idHistorialPaquete`),
  KEY `fk_historial_paquete_usuario` (`idUsuario`)
) ENGINE=MyISAM AUTO_INCREMENT=42 DEFAULT CHARSET=latin1;


DROP TABLE IF EXISTS `Historial_Pedido`;
CREATE TABLE `Historial_Pedido` (
  `idHistorialPedido` int(11) NOT NULL AUTO_INCREMENT,
  `idPedido` int(11) NOT NULL,
  `EstadoAnterior` enum('Pedido','Aprobado','Entregado','Finalizado') DEFAULT NULL,
  `EstadoNuevo` enum('Pedido','Aprobado','Entregado','Finalizado') NOT NULL,
  `FechaCambio` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `idUsuario` int(11) DEFAULT NULL,
  PRIMARY KEY (`idHistorialPedido`)
) ENGINE=InnoDB AUTO_INCREMENT=19 DEFAULT CHARSET=latin1;


DROP TABLE IF EXISTS `IInstrumento`;
CREATE TABLE `IInstrumento` (
  `idInstrumentoIndividual` int(11) NOT NULL AUTO_INCREMENT,
  `ultimaEsterilizacion` datetime NOT NULL,
  `Estado` enum('Disponible','En Uso','Limpieza','Pendiente','Autoclave') NOT NULL DEFAULT 'Disponible',
  `Ubicacion` enum('Almacen','Sala 1','Sala 2','Sala 3') NOT NULL DEFAULT 'Almacen',
  `idInstrumentoGrupo` int(11) NOT NULL,
  `idEquipo` int(11) DEFAULT NULL,
  `idPaquete` int(11) DEFAULT NULL,
  PRIMARY KEY (`idInstrumentoIndividual`),
  UNIQUE KEY `idEquipo` (`idEquipo`,`idPaquete`),
  KEY `FK_IInstrumento_GInstrumento` (`idInstrumentoGrupo`),
  KEY `FK_IInstrumento_Paquete` (`idPaquete`),
  CONSTRAINT `FK_IInstrumento_Equipo` FOREIGN KEY (`idEquipo`) REFERENCES `Equipo` (`idequipo`) ON DELETE SET NULL,
  CONSTRAINT `FK_IInstrumento_GInstrumento` FOREIGN KEY (`idInstrumentoGrupo`) REFERENCES `GInstrumento` (`idinstrumento`),
  CONSTRAINT `FK_IInstrumento_Paquete` FOREIGN KEY (`idPaquete`) REFERENCES `Paquete` (`idpaquete`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=158 DEFAULT CHARSET=latin1;


DELIMITER ;;

CREATE TRIGGER `trg_individual_insert` AFTER INSERT ON `IInstrumento` FOR EACH ROW
BEGIN
  INSERT INTO Historial_IInstrumento (
    idInstrumentoIndividual,
    fechaCambio,
    idUsuario,
    observaciones
  )
  VALUES (
    NEW.idInstrumentoIndividual,
    NOW(),
    @idUsuario,
    'INSERT'
  );
END;;

CREATE TRIGGER `trg_individual_update` AFTER UPDATE ON `IInstrumento` FOR EACH ROW
BEGIN
  DECLARE cambio TEXT DEFAULT '';

  -- Comparación de Estado
  IF OLD.Estado <> NEW.Estado THEN
    SET cambio = CONCAT(cambio, 'UPDATE: Estado ', OLD.Estado, '->', NEW.Estado, '
');
  END IF;
  
    -- Comparación de idPaquete
  IF OLD.idPaquete <> NEW.idPaquete THEN
    SET cambio = CONCAT(cambio, 'UPDATE: Paquete ', OLD.idPaquete, '->', NEW.idPaquete, '
');
  END IF;
  
    -- Comparación de idEquipo
  IF OLD.idEquipo <> NEW.idEquipo THEN
    SET cambio = CONCAT(cambio, 'UPDATE: Equipo ', OLD.idEquipo, '->', NEW.idEquipo, '
');
  END IF;

  -- Comparación de Ubicacion
  IF OLD.Ubicacion <> NEW.Ubicacion THEN
    SET cambio = CONCAT(cambio, 'UPDATE: Ubicacion ', OLD.Ubicacion, '->', NEW.Ubicacion, '
');
  END IF;

  -- Comparación de idInstrumentoGrupo
  IF OLD.idInstrumentoGrupo <> NEW.idInstrumentoGrupo THEN
    SET cambio = CONCAT(cambio, 'UPDATE: idInstrumentoGrupo ', OLD.idInstrumentoGrupo, '->', NEW.idInstrumentoGrupo, '
');
  END IF;

  -- Insertar historial si hay cambios
  IF cambio <> '' THEN
    INSERT INTO Historial_IInstrumento (
      idInstrumentoIndividual,
      fechaCambio,
      idUsuario,
      observaciones
    )
    VALUES (
      NEW.idInstrumentoIndividual,
      NOW(),
      @idUsuario,
      cambio
    );
  END IF;
END;;

CREATE TRIGGER `trg_individual_delete` AFTER DELETE ON `IInstrumento` FOR EACH ROW
BEGIN
  INSERT INTO Historial_IInstrumento (
    idInstrumentoIndividual,
    fechaCambio,
    idUsuario,
    observaciones
  )
  VALUES (
    OLD.idInstrumentoIndividual,
    NOW(),
    @idUsuario,
    'DELETE'
  );
END;;

DELIMITER ;

DROP TABLE IF EXISTS `Paquete`;
CREATE TABLE `Paquete` (
  `idPaquete` int(11) NOT NULL AUTO_INCREMENT,
  `Nombre` varchar(80) NOT NULL,
  `idEspecialidad` int(11) NOT NULL,
  PRIMARY KEY (`idPaquete`),
  KEY `FK_Paquete_Especialidad` (`idEspecialidad`),
  CONSTRAINT `FK_Paquete_Especialidad` FOREIGN KEY (`idEspecialidad`) REFERENCES `Especialidad` (`idespecialidad`)
) ENGINE=InnoDB AUTO_INCREMENT=15 DEFAULT CHARSET=latin1;


DELIMITER ;;

CREATE TRIGGER `trg_paquete_insert` AFTER INSERT ON `Paquete` FOR EACH ROW
BEGIN
  INSERT INTO Historial_Paquetes (
    idPaquete,
    fechaCambio,
    idUsuario,
    tipoOperacion,
    observaciones
  ) VALUES (
    NEW.idPaquete,
    NOW(),
    @idUsuario,
    'INSERT',
    'Nuevo paquete creado'
  );
END;;

CREATE TRIGGER `trg_paquete_update` AFTER UPDATE ON `Paquete` FOR EACH ROW
BEGIN
  IF OLD.Nombre <> NEW.Nombre THEN
    INSERT INTO Historial_Paquetes (
      idPaquete,
      fechaCambio,
      idUsuario,
      tipoOperacion,
      campo,
      valorAnterior,
      valorNuevo,
      observaciones
    ) VALUES (
      NEW.idPaquete,
      NOW(),
      @idUsuario,
      'UPDATE',
      'Nombre',
      OLD.Nombre,
      NEW.Nombre,
      CONCAT('Cambio de nombre: ', OLD.Nombre, ' -> ', NEW.Nombre)
    );
  END IF;

  IF OLD.idEspecialidad <> NEW.idEspecialidad THEN
    INSERT INTO Historial_Paquetes (
      idPaquete,
      fechaCambio,
      idUsuario,
      tipoOperacion,
      campo,
      valorAnterior,
      valorNuevo,
      observaciones
    ) VALUES (
      NEW.idPaquete,
      NOW(),
      @idUsuario,
      'UPDATE',
      'idEspecialidad',
      CAST(OLD.idEspecialidad AS CHAR),
      CAST(NEW.idEspecialidad AS CHAR),
      CONCAT('Cambio de idEspecialidad: ', OLD.idEspecialidad, ' -> ', NEW.idEspecialidad)
    );
  END IF;
END;;

CREATE TRIGGER `trg_paquete_delete` AFTER DELETE ON `Paquete` FOR EACH ROW
BEGIN
  INSERT INTO Historial_Paquetes (
    idPaquete,
    fechaCambio,
    idUsuario,
    tipoOperacion,
    observaciones
  ) VALUES (
    OLD.idPaquete,
    NOW(),
    @idUsuario,
    'DELETE',
    'Paquete eliminado'
  );
END;;

DELIMITER ;

DROP TABLE IF EXISTS `Paquete_Equipo`;
CREATE TABLE `Paquete_Equipo` (
  `idPaquete` int(11) NOT NULL,
  `idEquipo` int(11) NOT NULL,
  PRIMARY KEY (`idPaquete`,`idEquipo`),
  KEY `FK_PaqueteEquipo_Equipo` (`idEquipo`),
  CONSTRAINT `FK_PaqueteEquipo_Equipo` FOREIGN KEY (`idEquipo`) REFERENCES `Equipo` (`idequipo`),
  CONSTRAINT `FK_PaqueteEquipo_Paquete` FOREIGN KEY (`idPaquete`) REFERENCES `Paquete` (`idpaquete`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;


DELIMITER ;;

CREATE TRIGGER `trg_paquete_equipo_insert` AFTER INSERT ON `Paquete_Equipo` FOR EACH ROW
BEGIN
  INSERT INTO Historial_Paquetes (
    idPaquete,
    idEquipo,
    fechaCambio,
    idUsuario,
    tipoOperacion,
    observaciones
  ) VALUES (
    NEW.idPaquete,
    NEW.idEquipo,
    NOW(),
    @idUsuario,
    'INSERT',
    'Equipo agregado al paquete'
  );
END;;

CREATE TRIGGER `trg_paquete_equipo_delete` AFTER DELETE ON `Paquete_Equipo` FOR EACH ROW
BEGIN
  INSERT INTO Historial_Paquetes (
    idPaquete,
    idEquipo,
    fechaCambio,
    idUsuario,
    tipoOperacion,
    observaciones
  ) VALUES (
    OLD.idPaquete,
    OLD.idEquipo,
    NOW(),
    @idUsuario,
    'DELETE',
    'Equipo removido del paquete'
  );
END;;

DELIMITER ;

DROP TABLE IF EXISTS `Paquete_Instrumento`;
CREATE TABLE `Paquete_Instrumento` (
  `idPaquete` int(11) NOT NULL,
  `idInstrumento` int(11) NOT NULL,
  `cantidad` int(11) NOT NULL,
  PRIMARY KEY (`idPaquete`,`idInstrumento`),
  KEY `FK_PaqueteGInstrumento_GInstrumento` (`idInstrumento`),
  CONSTRAINT `FK_PaqueteGInstrumento_GInstrumento` FOREIGN KEY (`idInstrumento`) REFERENCES `GInstrumento` (`idinstrumento`),
  CONSTRAINT `FK_PaqueteGInstrumento_Paquete` FOREIGN KEY (`idPaquete`) REFERENCES `Paquete` (`idpaquete`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;


DELIMITER ;;

CREATE TRIGGER `trg_paquete_instrumento_insert` AFTER INSERT ON `Paquete_Instrumento` FOR EACH ROW
BEGIN
  INSERT INTO Historial_Paquetes (
    idPaquete,
    idInstrumento,
    fechaCambio,
    idUsuario,
    tipoOperacion,
    observaciones
  ) VALUES (
    NEW.idPaquete,
    NEW.idInstrumento,
    NOW(),
    @idUsuario,
    'INSERT',
    'Instrumento agregado al paquete'
  );
END;;

CREATE TRIGGER `trg_paquete_instrumento_update` AFTER UPDATE ON `Paquete_Instrumento` FOR EACH ROW
BEGIN
  IF OLD.cantidad <> NEW.cantidad THEN
    INSERT INTO Historial_Paquetes (
      idPaquete,
      idInstrumento,
      fechaCambio,
      idUsuario,
      tipoOperacion,
      campo,
      valorAnterior,
      valorNuevo,
      observaciones
    ) VALUES (
      NEW.idPaquete,
      NEW.idInstrumento,
      NOW(),
      @idUsuario,
      'UPDATE',
      'cantidad',
      OLD.cantidad,
      NEW.cantidad,
      CONCAT('Cantidad modificada: ', OLD.cantidad, ' -> ', NEW.cantidad)
    );
  END IF;
END;;

CREATE TRIGGER `trg_paquete_instrumento_delete` AFTER DELETE ON `Paquete_Instrumento` FOR EACH ROW
BEGIN
  INSERT INTO Historial_Paquetes (
    idPaquete,
    idInstrumento,
    fechaCambio,
    idUsuario,
    tipoOperacion,
    observaciones
  ) VALUES (
    OLD.idPaquete,
    OLD.idInstrumento,
    NOW(),
    @idUsuario,
    'DELETE',
    'Instrumento removido del paquete'
  );
END;;

DELIMITER ;

DROP TABLE IF EXISTS `Pedido`;
CREATE TABLE `Pedido` (
  `idPedido` int(11) NOT NULL AUTO_INCREMENT,
  `Fecha` date NOT NULL,
  `Hora` time NOT NULL,
  `Ubicacion` enum('Almacen','Sala 1','Sala 2','Sala 3') NOT NULL DEFAULT 'Almacen',
  `Cirugia` varchar(40) NOT NULL,
  `Estado` enum('Pedido','Aprobado','Entregado','Finalizado') NOT NULL DEFAULT 'Pedido',
  `idEnfermero` int(11) NOT NULL,
  `idPaquete` int(11) NOT NULL,
  PRIMARY KEY (`idPedido`),
  KEY `FK_Pedido_Enfermero` (`idEnfermero`),
  KEY `FK_Pedido_Paquete` (`idPaquete`),
  CONSTRAINT `FK_Pedido_Enfermero` FOREIGN KEY (`idEnfermero`) REFERENCES `Usuario` (`idusuario`),
  CONSTRAINT `FK_Pedido_Paquete` FOREIGN KEY (`idPaquete`) REFERENCES `Paquete` (`idpaquete`)
) ENGINE=InnoDB AUTO_INCREMENT=18 DEFAULT CHARSET=latin1;


DELIMITER ;;

CREATE TRIGGER `trg_Pedido_insert` AFTER INSERT ON `Pedido` FOR EACH ROW
BEGIN
  INSERT INTO Historial_Pedido (
    idPedido,
    EstadoAnterior,
    EstadoNuevo,
    FechaCambio,
    idUsuario
  )
  VALUES (
    NEW.idPedido,
    NULL,
    NEW.Estado,
    NOW(),
    @idUsuario
  );
END;;

CREATE TRIGGER `trg_Pedido_estado_update` AFTER UPDATE ON `Pedido` FOR EACH ROW
BEGIN
  IF OLD.Estado <> NEW.Estado THEN
    INSERT INTO Historial_Pedido (
      idPedido,
      EstadoAnterior,
      EstadoNuevo,
      FechaCambio,
      idUsuario
    )
    VALUES (
      NEW.idPedido,
      OLD.Estado,
      NEW.Estado,
      NOW(),
      @idUsuario
    );
  END IF;
END;;

CREATE TRIGGER `trg_Pedido_delete` AFTER DELETE ON `Pedido` FOR EACH ROW
BEGIN
  INSERT INTO Historial_Pedido (
    idPedido,
    EstadoAnterior,
    EstadoNuevo,
    FechaCambio,
    idUsuario
  )
  VALUES (
    OLD.idPedido,
    OLD.Estado,
    'Eliminado',  -- o puedes usar NULL si prefieres no establecer un "estado nuevo"
    NOW(),
    @idUsuario
  );
END;;

DELIMITER ;

DROP TABLE IF EXISTS `Pedido_Equipo`;
CREATE TABLE `Pedido_Equipo` (
  `idPedido` int(11) NOT NULL,
  `idEquipo` int(11) NOT NULL,
  PRIMARY KEY (`idPedido`,`idEquipo`),
  CONSTRAINT `FK_PedidoEquipo_Equipo` FOREIGN KEY (`idPedido`) REFERENCES `Pedido` (`idpedido`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=latin1;


DROP TABLE IF EXISTS `Pedido_IInstrumento`;
CREATE TABLE `Pedido_IInstrumento` (
  `idPedido` int(11) NOT NULL,
  `idInstrumento` int(11) NOT NULL,
  PRIMARY KEY (`idPedido`,`idInstrumento`),
  CONSTRAINT `FK_PedidoGInstrumento_GInstrumento` FOREIGN KEY (`idPedido`) REFERENCES `Pedido` (`idpedido`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=latin1;


DROP TABLE IF EXISTS `Usuario`;
CREATE TABLE `Usuario` (
  `idUsuario` int(11) NOT NULL AUTO_INCREMENT,
  `Nombres` varchar(45) NOT NULL,
  `ApellidoPaterno` varchar(20) NOT NULL,
  `ApellidoMaterno` varchar(20) DEFAULT NULL,
  `Rol` enum('Administrador','Almacenista','Enfermero') NOT NULL,
  `Alias` varchar(30) DEFAULT NULL,
  `Correo` varchar(40) NOT NULL,
  `Contrasena` varchar(64) NOT NULL,
  PRIMARY KEY (`idUsuario`)
) ENGINE=InnoDB AUTO_INCREMENT=16 DEFAULT CHARSET=utf8;


-- 2011-09-05 21:25:09
