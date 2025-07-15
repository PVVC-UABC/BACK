-- Adminer 4.8.1 MySQL 8.0.3-rc-log dump

SET NAMES utf8;
SET time_zone = '+00:00';
SET foreign_key_checks = 0;
SET sql_mode = 'NO_AUTO_VALUE_ON_ZERO';

DROP TABLE IF EXISTS `Equipo`;
CREATE TABLE `Equipo` (
  `idEquipo` int(11) NOT NULL AUTO_INCREMENT,
  `Nombre` varchar(80) NOT NULL,
  PRIMARY KEY (`idEquipo`)
) ENGINE=InnoDB AUTO_INCREMENT=14 DEFAULT CHARSET=latin1;

INSERT INTO `Equipo` (`idEquipo`, `Nombre`) VALUES
(1,	'Equipo de Estrabismo'),
(9,	'Equipo Prueba'),
(12,	'Prueba otra'),
(13,	'Prueba 2');

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

INSERT INTO `Equipo_Instrumento` (`idEquipo`, `idInstrumento`, `cantidad`) VALUES
(1,	2,	4),
(1,	10,	2),
(9,	26,	2),
(12,	26,	2);

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

INSERT INTO `Especialidad` (`idEspecialidad`, `Nombre`) VALUES
(1,	'Pediatria'),
(2,	'Cirugia'),
(5,	'Cirugia2'),
(6,	'Odontopediatria'),
(7,	'Cirugía Gastrointestinal'),
(8,	'Neumologia'),
(10,	'Otorrinolaringologia'),
(11,	'Cirugia Pediatrica'),
(12,	'Cirugia Plastica'),
(13,	'Cirugia Vascular');

DROP TABLE IF EXISTS `GInstrumento`;
CREATE TABLE `GInstrumento` (
  `idInstrumento` int(11) NOT NULL AUTO_INCREMENT,
  `CodigoDeBarras` varchar(15) NOT NULL,
  `Cantidad` int(11) NOT NULL,
  `Nombre` varchar(80) NOT NULL,
  PRIMARY KEY (`idInstrumento`)
) ENGINE=InnoDB AUTO_INCREMENT=27 DEFAULT CHARSET=latin1 COMMENT='Objeto de Instrumentos como Grupo';

INSERT INTO `GInstrumento` (`idInstrumento`, `CodigoDeBarras`, `Cantidad`, `Nombre`) VALUES
(2,	'123456',	4,	'Lupa'),
(3,	'1234',	4,	'Tijeras'),
(4,	'123345',	2,	'Tijeras X'),
(5,	'12344567',	0,	'Pinzas'),
(6,	'55555',	10,	'Pinzas X'),
(8,	'7777',	0,	'Tijeras Z'),
(10,	'9999',	0,	'Hilo para sutura'),
(26,	'123456789',	20,	'CELULARES');

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

INSERT INTO `Historial_Equipos` (`idHistorialEquipo`, `idEquipo`, `idInstrumento`, `fechaCambio`, `idUsuario`, `tipoOperacion`, `campo`, `valorAnterior`, `valorNuevo`, `observaciones`, `nombreEquipoPrevio`) VALUES
(1,	1,	NULL,	'2025-05-22 17:18:38',	NULL,	'INSERT',	NULL,	NULL,	NULL,	'Nuevo equipo creado',	''),
(2,	1,	1,	'2025-05-22 18:09:35',	NULL,	'INSERT',	NULL,	NULL,	NULL,	'Instrumento agregado al equipo',	''),
(3,	1,	2,	'2025-05-22 18:23:17',	NULL,	'INSERT',	NULL,	NULL,	NULL,	'Instrumento agregado al equipo',	''),
(4,	2,	NULL,	'2025-05-26 02:55:09',	NULL,	'INSERT',	NULL,	NULL,	NULL,	'Nuevo equipo creado',	''),
(5,	3,	NULL,	'2025-05-26 02:55:51',	NULL,	'INSERT',	NULL,	NULL,	NULL,	'Nuevo equipo creado',	''),
(6,	4,	NULL,	'2025-05-26 02:57:57',	NULL,	'INSERT',	NULL,	NULL,	NULL,	'Nuevo equipo creado',	''),
(7,	5,	NULL,	'2025-05-26 03:03:20',	NULL,	'INSERT',	NULL,	NULL,	NULL,	'Nuevo equipo creado',	''),
(8,	4,	NULL,	'2025-05-26 03:16:53',	NULL,	'DELETE',	NULL,	NULL,	NULL,	'Equipo eliminado',	''),
(9,	3,	NULL,	'2025-05-26 03:17:20',	NULL,	'DELETE',	NULL,	NULL,	NULL,	'Equipo eliminado',	''),
(10,	6,	NULL,	'2025-05-26 03:23:37',	NULL,	'INSERT',	NULL,	NULL,	NULL,	'Nuevo equipo creado',	''),
(11,	6,	NULL,	'2025-05-26 03:26:20',	NULL,	'UPDATE',	'Nombre',	'Equipo de Ortopedia',	'Equipo de Ortopedia xd',	'Cambio de nombre: Equipo de Ortopedia -> Equipo de Ortopedia xd',	''),
(12,	6,	NULL,	'2025-05-26 03:33:05',	NULL,	'UPDATE',	'Nombre',	'Equipo de Ortopedia xd',	'Equipo de Ortopedia',	'Cambio de nombre: Equipo de Ortopedia xd -> Equipo de Ortopedia',	''),
(13,	1,	NULL,	'2025-05-26 15:34:11',	NULL,	'UPDATE',	'Nombre',	'Equipo de oftalmologia',	'Equipo de Estrabismo 1',	'Cambio de nombre: Equipo de oftalmologia -> Equipo de Estrabismo 1',	''),
(14,	1,	NULL,	'2025-05-28 23:00:38',	NULL,	'UPDATE',	'Nombre',	'Equipo de Estrabismo 1',	'Equipo de Estrabismo',	'Cambio de nombre: Equipo de Estrabismo 1 -> Equipo de Estrabismo',	''),
(15,	1,	NULL,	'2025-05-28 23:00:59',	NULL,	'UPDATE',	'Nombre',	'Equipo de Estrabismo',	'Equipo de Estrabismo 1',	'Cambio de nombre: Equipo de Estrabismo -> Equipo de Estrabismo 1',	''),
(16,	6,	NULL,	'2025-05-28 23:01:24',	NULL,	'DELETE',	NULL,	NULL,	NULL,	'Equipo eliminado',	''),
(17,	7,	NULL,	'2025-05-28 23:03:27',	NULL,	'INSERT',	NULL,	NULL,	NULL,	'Nuevo equipo creado',	''),
(18,	1,	NULL,	'2025-05-28 23:03:39',	NULL,	'UPDATE',	'Nombre',	'Equipo de Estrabismo 1',	'Equipo de Estrabismo',	'Cambio de nombre: Equipo de Estrabismo 1 -> Equipo de Estrabismo',	''),
(19,	7,	NULL,	'2025-05-28 23:27:28',	NULL,	'DELETE',	NULL,	NULL,	NULL,	'Equipo eliminado',	''),
(20,	1,	NULL,	'2025-05-29 00:44:59',	NULL,	'UPDATE',	'Nombre',	'Equipo de Estrabismo',	'Equipo de Estrabismo 1',	'Cambio de nombre: Equipo de Estrabismo -> Equipo de Estrabismo 1',	''),
(21,	1,	NULL,	'2025-05-29 00:45:15',	NULL,	'UPDATE',	'Nombre',	'Equipo de Estrabismo 1',	'Equipo de Estrabismo',	'Cambio de nombre: Equipo de Estrabismo 1 -> Equipo de Estrabismo',	''),
(22,	8,	NULL,	'2025-05-29 00:45:22',	NULL,	'INSERT',	NULL,	NULL,	NULL,	'Nuevo equipo creado',	''),
(23,	8,	NULL,	'2025-05-29 00:45:29',	NULL,	'DELETE',	NULL,	NULL,	NULL,	'Equipo eliminado',	''),
(24,	1,	10,	'2011-07-21 01:09:05',	NULL,	'INSERT',	NULL,	NULL,	NULL,	'Instrumento agregado al equipo',	''),
(25,	1,	1,	'2011-07-21 02:29:44',	NULL,	'DELETE',	NULL,	NULL,	NULL,	'Instrumento removido del equipo',	''),
(26,	1,	1,	'2011-07-21 02:30:09',	NULL,	'DELETE',	NULL,	NULL,	NULL,	'Instrumento removido del equipo',	''),
(27,	2,	3,	'2011-07-21 02:40:00',	NULL,	'INSERT',	NULL,	NULL,	NULL,	'Instrumento agregado al equipo',	''),
(28,	2,	3,	'2011-07-21 02:45:48',	NULL,	'UPDATE',	'cantidad',	'4',	'3',	'Cantidad modificada: 4 -> 3',	''),
(29,	2,	3,	'2011-07-21 02:46:05',	NULL,	'UPDATE',	'cantidad',	'3',	'4',	'Cantidad modificada: 3 -> 4',	''),
(30,	2,	3,	'2011-07-21 02:46:51',	NULL,	'UPDATE',	'cantidad',	'4',	'3',	'Cantidad modificada: 4 -> 3',	''),
(31,	2,	3,	'2011-07-21 03:01:18',	NULL,	'DELETE',	NULL,	NULL,	NULL,	'Instrumento removido del equipo',	''),
(32,	2,	NULL,	'2011-07-21 03:01:18',	NULL,	'DELETE',	NULL,	NULL,	NULL,	'Equipo eliminado',	''),
(33,	5,	NULL,	'2011-07-21 03:07:06',	NULL,	'DELETE',	NULL,	NULL,	NULL,	'Equipo eliminado',	''),
(34,	9,	NULL,	'2011-07-21 03:07:43',	NULL,	'INSERT',	NULL,	NULL,	NULL,	'Nuevo equipo creado',	''),
(35,	9,	3,	'2011-07-21 03:07:49',	NULL,	'INSERT',	NULL,	NULL,	NULL,	'Instrumento agregado al equipo',	''),
(36,	9,	3,	'2011-07-21 03:10:39',	NULL,	'DELETE',	NULL,	NULL,	NULL,	'Instrumento removido del equipo',	''),
(37,	9,	11,	'2011-07-21 04:10:53',	NULL,	'INSERT',	NULL,	NULL,	NULL,	'Instrumento agregado al equipo',	''),
(38,	9,	11,	'2011-07-21 04:11:23',	NULL,	'DELETE',	NULL,	NULL,	NULL,	'Instrumento removido del equipo',	''),
(39,	10,	NULL,	'2011-07-21 06:15:08',	NULL,	'INSERT',	NULL,	NULL,	NULL,	'Nuevo equipo creado',	'EDuardo'),
(40,	10,	NULL,	'2011-07-21 06:15:31',	NULL,	'DELETE',	NULL,	NULL,	NULL,	'Equipo eliminado',	''),
(41,	11,	NULL,	'2011-07-21 07:13:05',	NULL,	'INSERT',	NULL,	NULL,	NULL,	'Nuevo equipo creado',	'EDuardo'),
(42,	11,	9,	'2011-07-21 07:14:31',	NULL,	'INSERT',	NULL,	NULL,	NULL,	'Instrumento agregado al equipo',	'EDuardo'),
(43,	11,	9,	'2011-07-21 07:15:07',	NULL,	'DELETE',	NULL,	NULL,	NULL,	'Instrumento removido del equipo',	''),
(44,	11,	NULL,	'2011-07-21 07:15:07',	NULL,	'DELETE',	NULL,	NULL,	NULL,	'Equipo eliminado',	''),
(45,	12,	NULL,	'2011-07-21 15:43:39',	NULL,	'INSERT',	NULL,	NULL,	NULL,	'Nuevo equipo creado',	''),
(46,	12,	NULL,	'2011-07-21 15:44:14',	NULL,	'UPDATE',	'Nombre',	'Prueba 2',	'Prueba otra',	'Cambio de nombre: Prueba 2 -> Prueba otra',	''),
(47,	12,	26,	'2011-07-21 15:46:19',	NULL,	'INSERT',	NULL,	NULL,	NULL,	'Instrumento agregado al equipo',	''),
(48,	12,	26,	'2011-07-21 15:46:37',	NULL,	'UPDATE',	'cantidad',	'5',	'9',	'Cantidad modificada: 5 -> 9',	''),
(49,	12,	26,	'2011-07-21 15:47:06',	NULL,	'UPDATE',	'cantidad',	'9',	'15',	'Cantidad modificada: 9 -> 15',	''),
(50,	12,	26,	'2011-07-21 15:50:02',	NULL,	'UPDATE',	'cantidad',	'15',	'6',	'Cantidad modificada: 15 -> 6',	''),
(51,	9,	26,	'2011-07-21 15:53:59',	NULL,	'INSERT',	NULL,	NULL,	NULL,	'Instrumento agregado al equipo',	''),
(52,	9,	26,	'2011-07-21 15:57:11',	NULL,	'UPDATE',	'cantidad',	'6',	'12',	'Cantidad modificada: 6 -> 12',	''),
(53,	9,	26,	'2011-07-21 15:57:29',	NULL,	'UPDATE',	'cantidad',	'12',	'2',	'Cantidad modificada: 12 -> 2',	''),
(54,	12,	26,	'2011-07-21 16:08:45',	NULL,	'UPDATE',	'cantidad',	'6',	'2',	'Cantidad modificada: 6 -> 2',	''),
(55,	13,	NULL,	'2011-07-21 16:26:43',	NULL,	'INSERT',	NULL,	NULL,	NULL,	'Nuevo equipo creado',	'');

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

INSERT INTO `Historial_GInstrumento` (`idHistorial`, `idInstrumento`, `fechaCambio`, `idUsuario`, `observaciones`, `nombreInstrumentoPrevio`) VALUES
(1,	1,	'2025-05-22 17:19:49',	NULL,	'INSERT',	''),
(2,	2,	'2025-05-22 18:22:31',	NULL,	'INSERT',	''),
(3,	3,	'2025-05-26 15:26:34',	NULL,	'INSERT',	''),
(4,	4,	'2025-05-26 15:27:13',	NULL,	'INSERT',	''),
(5,	5,	'2025-05-26 15:35:09',	NULL,	'INSERT',	''),
(6,	6,	'2025-05-26 15:36:54',	NULL,	'INSERT',	''),
(7,	7,	'2025-05-26 15:38:16',	NULL,	'INSERT',	'Tijeras Y'),
(8,	7,	'2025-05-26 15:40:23',	NULL,	'UPDATE: Cantidad 2->0\n',	'Tijeras Y'),
(9,	7,	'2025-05-26 15:42:38',	NULL,	'UPDATE: Cantidad 0->2\n',	'Tijeras Y'),
(10,	7,	'2025-05-26 15:46:15',	NULL,	'UPDATE: Cantidad 2->0\n',	'Tijeras Y'),
(11,	7,	'2025-05-26 15:47:28',	NULL,	'UPDATE: Cantidad 0->2\n',	'Tijeras Y'),
(12,	7,	'2025-05-26 15:49:04',	NULL,	'UPDATE: Cantidad 2->0\n',	'Tijeras Y'),
(13,	8,	'2025-05-26 15:50:30',	NULL,	'INSERT',	''),
(14,	8,	'2025-05-26 15:50:46',	NULL,	'UPDATE: Cantidad 3->0\n',	''),
(15,	9,	'2025-05-29 01:02:48',	NULL,	'INSERT',	'Bisturi X'),
(16,	10,	'2025-05-29 18:41:39',	NULL,	'INSERT',	''),
(17,	11,	'2011-07-21 01:53:51',	NULL,	'INSERT',	''),
(18,	5,	'2011-07-21 02:15:29',	NULL,	'UPDATE: Cantidad 2->10\n',	''),
(19,	11,	'2011-07-21 02:18:19',	NULL,	'UPDATE: Cantidad 5->10\n',	''),
(20,	11,	'2011-07-21 02:18:35',	NULL,	'UPDATE: Cantidad 10->4\n',	''),
(21,	11,	'2011-07-21 02:18:51',	NULL,	'UPDATE: Cantidad 4->1\n',	''),
(22,	10,	'2011-07-21 02:19:22',	NULL,	'UPDATE: Cantidad 2->0\n',	''),
(23,	5,	'2011-07-21 02:21:15',	NULL,	'UPDATE: Cantidad 10->1\n',	''),
(24,	5,	'2011-07-21 02:21:26',	NULL,	'UPDATE: Cantidad 1->10\n',	''),
(25,	6,	'2011-07-21 02:21:41',	NULL,	'UPDATE: Cantidad 3->10\n',	''),
(26,	1,	'2011-07-21 02:30:10',	NULL,	'DELETE',	''),
(27,	11,	'2011-07-21 04:12:19',	NULL,	'DELETE',	''),
(28,	12,	'2011-07-21 04:42:47',	NULL,	'INSERT',	''),
(29,	12,	'2011-07-21 04:47:31',	NULL,	'DELETE',	''),
(30,	13,	'2011-07-21 04:50:38',	NULL,	'INSERT',	''),
(31,	13,	'2011-07-21 04:51:11',	NULL,	'DELETE',	''),
(32,	14,	'2011-07-21 04:52:09',	NULL,	'INSERT',	''),
(33,	14,	'2011-07-21 04:52:26',	NULL,	'DELETE',	''),
(34,	15,	'2011-07-21 04:53:44',	NULL,	'INSERT',	''),
(35,	15,	'2011-07-21 04:54:00',	NULL,	'DELETE',	''),
(36,	16,	'2011-07-21 04:56:32',	NULL,	'INSERT',	''),
(37,	16,	'2011-07-21 04:56:50',	NULL,	'DELETE',	''),
(38,	17,	'2011-07-21 05:00:01',	NULL,	'INSERT',	''),
(39,	17,	'2011-07-21 05:00:26',	NULL,	'DELETE',	''),
(40,	18,	'2011-07-21 05:16:10',	NULL,	'INSERT',	''),
(41,	18,	'2011-07-21 05:16:31',	NULL,	'DELETE',	''),
(42,	19,	'2011-07-21 05:19:16',	NULL,	'INSERT',	''),
(43,	19,	'2011-07-21 05:19:23',	NULL,	'DELETE',	''),
(44,	20,	'2011-07-21 05:27:43',	NULL,	'INSERT',	''),
(45,	20,	'2011-07-21 05:27:55',	NULL,	'DELETE',	''),
(46,	21,	'2011-07-21 05:31:24',	NULL,	'INSERT',	''),
(47,	21,	'2011-07-21 05:31:36',	NULL,	'DELETE',	''),
(48,	22,	'2011-07-21 05:38:59',	NULL,	'INSERT',	''),
(49,	22,	'2011-07-21 05:41:48',	NULL,	'DELETE',	'Tijeras'),
(50,	22,	'2011-07-21 05:41:49',	NULL,	'DELETE',	''),
(51,	23,	'2011-07-21 05:55:36',	NULL,	'INSERT',	''),
(52,	23,	'2011-07-21 05:55:43',	NULL,	'DELETE',	'Tijeras'),
(53,	23,	'2011-07-21 05:55:43',	NULL,	'DELETE',	''),
(54,	24,	'2011-07-21 05:59:04',	NULL,	'INSERT',	'Tijeras'),
(55,	24,	'2011-07-21 05:59:10',	NULL,	'DELETE',	''),
(56,	25,	'2011-07-21 05:59:28',	NULL,	'INSERT',	'POPO'),
(57,	25,	'2011-07-21 05:59:36',	NULL,	'DELETE',	''),
(58,	9,	'2011-07-21 07:16:06',	NULL,	'DELETE',	''),
(59,	26,	'2011-07-21 15:35:45',	NULL,	'INSERT',	''),
(60,	5,	'2011-07-21 15:38:30',	NULL,	'UPDATE: Cantidad 10->1\n',	''),
(61,	5,	'2011-07-21 15:42:13',	NULL,	'UPDATE: Cantidad 1->0\n',	''),
(62,	7,	'2011-07-21 15:43:00',	NULL,	'DELETE',	'');

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

INSERT INTO `Historial_IInstrumento` (`idHistorialIndividual`, `idInstrumentoIndividual`, `fechaCambio`, `idUsuario`, `observaciones`, `nombreHerramientaPrevio`) VALUES
(1,	2,	'2025-05-22 18:09:11',	NULL,	'INSERT',	''),
(2,	3,	'2025-05-22 18:22:53',	NULL,	'INSERT',	''),
(3,	4,	'2025-05-26 15:26:34',	NULL,	'INSERT',	''),
(4,	5,	'2025-05-26 15:26:34',	NULL,	'INSERT',	''),
(5,	6,	'2025-05-26 15:26:34',	NULL,	'INSERT',	''),
(6,	7,	'2025-05-26 15:26:34',	NULL,	'INSERT',	''),
(7,	8,	'2025-05-26 15:27:13',	NULL,	'INSERT',	''),
(8,	9,	'2025-05-26 15:27:13',	NULL,	'INSERT',	''),
(9,	10,	'2025-05-26 15:35:09',	NULL,	'INSERT',	''),
(10,	11,	'2025-05-26 15:35:09',	NULL,	'INSERT',	''),
(11,	12,	'2025-05-26 15:36:54',	NULL,	'INSERT',	''),
(12,	13,	'2025-05-26 15:36:54',	NULL,	'INSERT',	''),
(13,	14,	'2025-05-26 15:36:54',	NULL,	'INSERT',	''),
(14,	15,	'2025-05-26 15:38:16',	NULL,	'INSERT',	'Hilo para sutura'),
(15,	16,	'2025-05-26 15:38:16',	NULL,	'INSERT',	''),
(16,	15,	'2025-05-26 15:40:23',	NULL,	'DELETE',	'Hilo para sutura'),
(17,	16,	'2025-05-26 15:40:23',	NULL,	'DELETE',	''),
(18,	17,	'2025-05-26 15:42:38',	NULL,	'INSERT',	''),
(19,	18,	'2025-05-26 15:42:38',	NULL,	'INSERT',	''),
(20,	17,	'2025-05-26 15:46:15',	NULL,	'DELETE',	''),
(21,	18,	'2025-05-26 15:46:15',	NULL,	'DELETE',	''),
(22,	19,	'2025-05-26 15:47:28',	NULL,	'INSERT',	''),
(23,	20,	'2025-05-26 15:47:28',	NULL,	'INSERT',	''),
(24,	19,	'2025-05-26 15:49:04',	NULL,	'DELETE',	''),
(25,	20,	'2025-05-26 15:49:04',	NULL,	'DELETE',	''),
(26,	21,	'2025-05-26 15:50:30',	NULL,	'INSERT',	''),
(27,	22,	'2025-05-26 15:50:30',	NULL,	'INSERT',	''),
(28,	23,	'2025-05-26 15:50:30',	NULL,	'INSERT',	''),
(29,	21,	'2025-05-26 15:50:46',	NULL,	'DELETE',	''),
(30,	22,	'2025-05-26 15:50:46',	NULL,	'DELETE',	''),
(31,	23,	'2025-05-26 15:50:46',	NULL,	'DELETE',	''),
(32,	24,	'2025-05-29 01:02:48',	NULL,	'INSERT',	'Bisturi X'),
(33,	25,	'2025-05-29 01:02:48',	NULL,	'INSERT',	'Bisturi X'),
(34,	26,	'2025-05-29 01:02:48',	NULL,	'INSERT',	'Bisturi X'),
(35,	10,	'2025-05-29 12:43:02',	NULL,	'UPDATE: Estado Disponible->En Uso\n',	''),
(36,	11,	'2025-05-29 12:44:34',	NULL,	'UPDATE: Estado Disponible->En Uso\n',	''),
(37,	8,	'2025-05-29 12:52:38',	NULL,	'UPDATE: Ubicacion Almacen->Sala 1\n',	''),
(38,	10,	'2025-05-29 12:54:04',	NULL,	'UPDATE: Estado En Uso->Disponible\n',	''),
(39,	10,	'2025-05-29 12:54:13',	NULL,	'UPDATE: Ubicacion Almacen->Sala 2\n',	''),
(40,	8,	'2025-05-29 13:39:46',	NULL,	'UPDATE: Ubicacion Sala 1->Sala 2\n',	''),
(41,	8,	'2025-05-29 13:40:05',	NULL,	'UPDATE: Ubicacion Sala 2->Sala 1\n',	''),
(42,	11,	'2025-05-29 13:45:01',	NULL,	'UPDATE: Estado En Uso->Disponible\n',	''),
(43,	9,	'2025-05-29 15:33:10',	NULL,	'UPDATE: Estado Disponible->En Uso\nUPDATE: Ubicacion Almacen->Sala 1\n',	''),
(44,	3,	'2025-05-29 16:37:49',	NULL,	'UPDATE: Estado Disponible->En Uso\n',	''),
(45,	4,	'2025-05-29 16:39:24',	NULL,	'UPDATE: Estado Disponible->Limpieza\n',	''),
(46,	5,	'2025-05-29 16:40:57',	NULL,	'UPDATE: Estado Disponible->Pendiente\n',	''),
(47,	10,	'2025-05-29 17:06:30',	NULL,	'UPDATE: Estado Disponible->Limpieza\n',	''),
(48,	27,	'2025-05-29 18:41:39',	NULL,	'INSERT',	''),
(49,	28,	'2025-05-29 18:41:39',	NULL,	'INSERT',	''),
(50,	2,	'2011-07-21 01:15:19',	NULL,	'UPDATE: Ubicacion Almacen->Sala 1\n',	''),
(51,	2,	'2011-07-21 01:17:56',	NULL,	'UPDATE: Equipo 2->5\n',	''),
(52,	29,	'2011-07-21 01:53:51',	NULL,	'INSERT',	''),
(53,	30,	'2011-07-21 01:53:51',	NULL,	'INSERT',	''),
(54,	31,	'2011-07-21 01:53:51',	NULL,	'INSERT',	''),
(55,	32,	'2011-07-21 01:53:51',	NULL,	'INSERT',	''),
(56,	33,	'2011-07-21 01:53:51',	NULL,	'INSERT',	''),
(57,	34,	'2011-07-21 02:15:29',	NULL,	'INSERT',	''),
(58,	35,	'2011-07-21 02:15:29',	NULL,	'INSERT',	''),
(59,	36,	'2011-07-21 02:15:29',	NULL,	'INSERT',	''),
(60,	37,	'2011-07-21 02:15:29',	NULL,	'INSERT',	''),
(61,	38,	'2011-07-21 02:15:29',	NULL,	'INSERT',	''),
(62,	39,	'2011-07-21 02:15:29',	NULL,	'INSERT',	''),
(63,	40,	'2011-07-21 02:15:29',	NULL,	'INSERT',	''),
(64,	41,	'2011-07-21 02:15:29',	NULL,	'INSERT',	''),
(65,	33,	'2011-07-21 02:18:01',	NULL,	'UPDATE: Estado Disponible->En Uso\n',	''),
(66,	42,	'2011-07-21 02:18:18',	NULL,	'INSERT',	''),
(67,	43,	'2011-07-21 02:18:18',	NULL,	'INSERT',	''),
(68,	44,	'2011-07-21 02:18:18',	NULL,	'INSERT',	''),
(69,	45,	'2011-07-21 02:18:19',	NULL,	'INSERT',	''),
(70,	46,	'2011-07-21 02:18:19',	NULL,	'INSERT',	''),
(71,	29,	'2011-07-21 02:18:34',	NULL,	'DELETE',	''),
(72,	30,	'2011-07-21 02:18:34',	NULL,	'DELETE',	''),
(73,	31,	'2011-07-21 02:18:34',	NULL,	'DELETE',	''),
(74,	32,	'2011-07-21 02:18:35',	NULL,	'DELETE',	''),
(75,	42,	'2011-07-21 02:18:35',	NULL,	'DELETE',	''),
(76,	43,	'2011-07-21 02:18:35',	NULL,	'DELETE',	''),
(77,	44,	'2011-07-21 02:18:51',	NULL,	'DELETE',	''),
(78,	45,	'2011-07-21 02:18:51',	NULL,	'DELETE',	''),
(79,	46,	'2011-07-21 02:18:51',	NULL,	'DELETE',	''),
(80,	27,	'2011-07-21 02:19:22',	NULL,	'DELETE',	''),
(81,	28,	'2011-07-21 02:19:22',	NULL,	'DELETE',	''),
(82,	11,	'2011-07-21 02:21:14',	NULL,	'DELETE',	''),
(83,	34,	'2011-07-21 02:21:14',	NULL,	'DELETE',	''),
(84,	35,	'2011-07-21 02:21:14',	NULL,	'DELETE',	''),
(85,	36,	'2011-07-21 02:21:14',	NULL,	'DELETE',	''),
(86,	37,	'2011-07-21 02:21:14',	NULL,	'DELETE',	''),
(87,	38,	'2011-07-21 02:21:14',	NULL,	'DELETE',	''),
(88,	39,	'2011-07-21 02:21:14',	NULL,	'DELETE',	''),
(89,	40,	'2011-07-21 02:21:15',	NULL,	'DELETE',	''),
(90,	41,	'2011-07-21 02:21:15',	NULL,	'DELETE',	''),
(91,	47,	'2011-07-21 02:21:25',	NULL,	'INSERT',	''),
(92,	48,	'2011-07-21 02:21:25',	NULL,	'INSERT',	''),
(93,	49,	'2011-07-21 02:21:25',	NULL,	'INSERT',	''),
(94,	50,	'2011-07-21 02:21:25',	NULL,	'INSERT',	''),
(95,	51,	'2011-07-21 02:21:26',	NULL,	'INSERT',	''),
(96,	52,	'2011-07-21 02:21:26',	NULL,	'INSERT',	''),
(97,	53,	'2011-07-21 02:21:26',	NULL,	'INSERT',	''),
(98,	54,	'2011-07-21 02:21:26',	NULL,	'INSERT',	''),
(99,	55,	'2011-07-21 02:21:26',	NULL,	'INSERT',	''),
(100,	56,	'2011-07-21 02:21:40',	NULL,	'INSERT',	''),
(101,	57,	'2011-07-21 02:21:40',	NULL,	'INSERT',	''),
(102,	58,	'2011-07-21 02:21:40',	NULL,	'INSERT',	''),
(103,	59,	'2011-07-21 02:21:40',	NULL,	'INSERT',	''),
(104,	60,	'2011-07-21 02:21:40',	NULL,	'INSERT',	''),
(105,	61,	'2011-07-21 02:21:40',	NULL,	'INSERT',	''),
(106,	62,	'2011-07-21 02:21:40',	NULL,	'INSERT',	''),
(107,	2,	'2011-07-21 02:29:44',	NULL,	'DELETE',	''),
(108,	2,	'2011-07-21 02:30:09',	NULL,	'DELETE',	''),
(109,	7,	'2011-07-21 02:43:31',	NULL,	'UPDATE: Ubicacion Almacen->Sala 1\n',	''),
(110,	33,	'2011-07-21 04:12:19',	NULL,	'DELETE',	''),
(111,	63,	'2011-07-21 04:42:47',	NULL,	'INSERT',	''),
(112,	64,	'2011-07-21 04:42:47',	NULL,	'INSERT',	''),
(113,	65,	'2011-07-21 04:42:48',	NULL,	'INSERT',	''),
(114,	66,	'2011-07-21 04:42:48',	NULL,	'INSERT',	''),
(115,	67,	'2011-07-21 04:42:48',	NULL,	'INSERT',	''),
(116,	68,	'2011-07-21 04:42:48',	NULL,	'INSERT',	''),
(117,	69,	'2011-07-21 04:42:48',	NULL,	'INSERT',	''),
(118,	70,	'2011-07-21 04:42:48',	NULL,	'INSERT',	''),
(119,	71,	'2011-07-21 04:42:48',	NULL,	'INSERT',	''),
(120,	72,	'2011-07-21 04:42:48',	NULL,	'INSERT',	''),
(121,	63,	'2011-07-21 04:47:31',	NULL,	'DELETE',	''),
(122,	64,	'2011-07-21 04:47:31',	NULL,	'DELETE',	''),
(123,	65,	'2011-07-21 04:47:31',	NULL,	'DELETE',	''),
(124,	66,	'2011-07-21 04:47:31',	NULL,	'DELETE',	''),
(125,	67,	'2011-07-21 04:47:31',	NULL,	'DELETE',	''),
(126,	68,	'2011-07-21 04:47:31',	NULL,	'DELETE',	''),
(127,	69,	'2011-07-21 04:47:31',	NULL,	'DELETE',	''),
(128,	70,	'2011-07-21 04:47:31',	NULL,	'DELETE',	''),
(129,	71,	'2011-07-21 04:47:31',	NULL,	'DELETE',	''),
(130,	72,	'2011-07-21 04:47:31',	NULL,	'DELETE',	''),
(131,	73,	'2011-07-21 04:50:38',	NULL,	'INSERT',	''),
(132,	74,	'2011-07-21 04:50:38',	NULL,	'INSERT',	''),
(133,	75,	'2011-07-21 04:50:39',	NULL,	'INSERT',	''),
(134,	76,	'2011-07-21 04:50:39',	NULL,	'INSERT',	''),
(135,	77,	'2011-07-21 04:50:39',	NULL,	'INSERT',	''),
(136,	73,	'2011-07-21 04:51:11',	NULL,	'DELETE',	''),
(137,	74,	'2011-07-21 04:51:11',	NULL,	'DELETE',	''),
(138,	75,	'2011-07-21 04:51:11',	NULL,	'DELETE',	''),
(139,	76,	'2011-07-21 04:51:11',	NULL,	'DELETE',	''),
(140,	77,	'2011-07-21 04:51:11',	NULL,	'DELETE',	''),
(141,	78,	'2011-07-21 04:52:10',	NULL,	'INSERT',	''),
(142,	79,	'2011-07-21 04:52:10',	NULL,	'INSERT',	''),
(143,	80,	'2011-07-21 04:52:10',	NULL,	'INSERT',	''),
(144,	81,	'2011-07-21 04:52:10',	NULL,	'INSERT',	''),
(145,	82,	'2011-07-21 04:52:10',	NULL,	'INSERT',	''),
(146,	78,	'2011-07-21 04:52:26',	NULL,	'DELETE',	''),
(147,	79,	'2011-07-21 04:52:26',	NULL,	'DELETE',	''),
(148,	80,	'2011-07-21 04:52:26',	NULL,	'DELETE',	''),
(149,	81,	'2011-07-21 04:52:26',	NULL,	'DELETE',	''),
(150,	82,	'2011-07-21 04:52:26',	NULL,	'DELETE',	''),
(151,	83,	'2011-07-21 04:53:45',	NULL,	'INSERT',	''),
(152,	84,	'2011-07-21 04:53:45',	NULL,	'INSERT',	''),
(153,	85,	'2011-07-21 04:53:45',	NULL,	'INSERT',	''),
(154,	86,	'2011-07-21 04:53:45',	NULL,	'INSERT',	''),
(155,	87,	'2011-07-21 04:53:45',	NULL,	'INSERT',	''),
(156,	83,	'2011-07-21 04:53:59',	NULL,	'DELETE',	''),
(157,	84,	'2011-07-21 04:53:59',	NULL,	'DELETE',	''),
(158,	85,	'2011-07-21 04:53:59',	NULL,	'DELETE',	''),
(159,	86,	'2011-07-21 04:53:59',	NULL,	'DELETE',	''),
(160,	87,	'2011-07-21 04:53:59',	NULL,	'DELETE',	''),
(161,	88,	'2011-07-21 04:56:32',	NULL,	'INSERT',	''),
(162,	89,	'2011-07-21 04:56:32',	NULL,	'INSERT',	''),
(163,	90,	'2011-07-21 04:56:33',	NULL,	'INSERT',	''),
(164,	91,	'2011-07-21 04:56:33',	NULL,	'INSERT',	''),
(165,	92,	'2011-07-21 04:56:33',	NULL,	'INSERT',	''),
(166,	88,	'2011-07-21 04:56:49',	NULL,	'DELETE',	''),
(167,	89,	'2011-07-21 04:56:49',	NULL,	'DELETE',	''),
(168,	90,	'2011-07-21 04:56:49',	NULL,	'DELETE',	''),
(169,	91,	'2011-07-21 04:56:49',	NULL,	'DELETE',	''),
(170,	92,	'2011-07-21 04:56:49',	NULL,	'DELETE',	''),
(171,	93,	'2011-07-21 05:00:01',	NULL,	'INSERT',	'Instrumento de Cirugía'),
(172,	94,	'2011-07-21 05:00:01',	NULL,	'INSERT',	'Instrumento de Cirugía'),
(173,	95,	'2011-07-21 05:00:02',	NULL,	'INSERT',	'Instrumento de Cirugía'),
(174,	96,	'2011-07-21 05:00:02',	NULL,	'INSERT',	'Instrumento de Cirugía'),
(175,	97,	'2011-07-21 05:00:02',	NULL,	'INSERT',	'Instrumento de Cirugía'),
(176,	93,	'2011-07-21 05:00:26',	NULL,	'DELETE',	'Instrumento de Cirugía'),
(177,	94,	'2011-07-21 05:00:26',	NULL,	'DELETE',	'Instrumento de Cirugía'),
(178,	95,	'2011-07-21 05:00:26',	NULL,	'DELETE',	'Instrumento de Cirugía'),
(179,	96,	'2011-07-21 05:00:26',	NULL,	'DELETE',	'Instrumento de Cirugía'),
(180,	97,	'2011-07-21 05:00:26',	NULL,	'DELETE',	'Instrumento de Cirugía'),
(181,	98,	'2011-07-21 05:16:10',	NULL,	'INSERT',	'Instrumento de Cirugía'),
(182,	99,	'2011-07-21 05:16:11',	NULL,	'INSERT',	'Instrumento de Cirugía'),
(183,	100,	'2011-07-21 05:16:11',	NULL,	'INSERT',	'Instrumento de Cirugía'),
(184,	101,	'2011-07-21 05:16:11',	NULL,	'INSERT',	'Instrumento de Cirugía'),
(185,	102,	'2011-07-21 05:16:11',	NULL,	'INSERT',	'Instrumento de Cirugía'),
(186,	98,	'2011-07-21 05:16:31',	NULL,	'Eliminado',	'Instrumento de Cirugía'),
(187,	99,	'2011-07-21 05:16:31',	NULL,	'Eliminado',	'Instrumento de Cirugía'),
(188,	100,	'2011-07-21 05:16:31',	NULL,	'Eliminado',	'Instrumento de Cirugía'),
(189,	101,	'2011-07-21 05:16:31',	NULL,	'Eliminado',	'Instrumento de Cirugía'),
(190,	102,	'2011-07-21 05:16:31',	NULL,	'Eliminado',	'Instrumento de Cirugía'),
(191,	98,	'2011-07-21 05:16:31',	NULL,	'DELETE',	'Instrumento de Cirugía'),
(192,	99,	'2011-07-21 05:16:31',	NULL,	'DELETE',	'Instrumento de Cirugía'),
(193,	100,	'2011-07-21 05:16:31',	NULL,	'DELETE',	'Instrumento de Cirugía'),
(194,	101,	'2011-07-21 05:16:31',	NULL,	'DELETE',	'Instrumento de Cirugía'),
(195,	102,	'2011-07-21 05:16:31',	NULL,	'DELETE',	'Instrumento de Cirugía'),
(196,	103,	'2011-07-21 05:19:16',	NULL,	'INSERT',	'Instrumento de Cirugía'),
(197,	104,	'2011-07-21 05:19:16',	NULL,	'INSERT',	'Instrumento de Cirugía'),
(198,	105,	'2011-07-21 05:19:16',	NULL,	'INSERT',	'Instrumento de Cirugía'),
(199,	106,	'2011-07-21 05:19:16',	NULL,	'INSERT',	'Instrumento de Cirugía'),
(200,	107,	'2011-07-21 05:19:16',	NULL,	'INSERT',	'Instrumento de Cirugía'),
(201,	103,	'2011-07-21 05:19:23',	NULL,	'DELETE',	'Instrumento de Cirugía'),
(202,	104,	'2011-07-21 05:19:23',	NULL,	'DELETE',	'Instrumento de Cirugía'),
(203,	105,	'2011-07-21 05:19:23',	NULL,	'DELETE',	'Instrumento de Cirugía'),
(204,	106,	'2011-07-21 05:19:23',	NULL,	'DELETE',	'Instrumento de Cirugía'),
(205,	107,	'2011-07-21 05:19:23',	NULL,	'DELETE',	'Instrumento de Cirugía'),
(206,	108,	'2011-07-21 05:27:43',	NULL,	'INSERT',	'Instrumento de Cirugía'),
(207,	109,	'2011-07-21 05:27:43',	NULL,	'INSERT',	'Instrumento de Cirugía'),
(208,	110,	'2011-07-21 05:27:43',	NULL,	'INSERT',	'Instrumento de Cirugía'),
(209,	111,	'2011-07-21 05:27:43',	NULL,	'INSERT',	'Instrumento de Cirugía'),
(210,	112,	'2011-07-21 05:27:43',	NULL,	'INSERT',	'Instrumento de Cirugía'),
(211,	108,	'2011-07-21 05:27:55',	NULL,	'DELETE',	''),
(212,	109,	'2011-07-21 05:27:55',	NULL,	'DELETE',	''),
(213,	110,	'2011-07-21 05:27:55',	NULL,	'DELETE',	''),
(214,	111,	'2011-07-21 05:27:55',	NULL,	'DELETE',	''),
(215,	112,	'2011-07-21 05:27:55',	NULL,	'DELETE',	''),
(216,	113,	'2011-07-21 05:31:24',	NULL,	'INSERT',	'Tijeras'),
(217,	114,	'2011-07-21 05:31:25',	NULL,	'INSERT',	'Tijeras'),
(218,	115,	'2011-07-21 05:31:25',	NULL,	'INSERT',	'Tijeras'),
(219,	116,	'2011-07-21 05:31:25',	NULL,	'INSERT',	'Tijeras'),
(220,	117,	'2011-07-21 05:31:25',	NULL,	'INSERT',	'Tijeras'),
(221,	113,	'2011-07-21 05:31:35',	NULL,	'DELETE',	''),
(222,	114,	'2011-07-21 05:31:35',	NULL,	'DELETE',	''),
(223,	115,	'2011-07-21 05:31:35',	NULL,	'DELETE',	''),
(224,	116,	'2011-07-21 05:31:35',	NULL,	'DELETE',	''),
(225,	117,	'2011-07-21 05:31:35',	NULL,	'DELETE',	''),
(226,	118,	'2011-07-21 05:38:59',	NULL,	'INSERT',	'Tijeras'),
(227,	119,	'2011-07-21 05:38:59',	NULL,	'INSERT',	'Tijeras'),
(228,	120,	'2011-07-21 05:38:59',	NULL,	'INSERT',	'Tijeras'),
(229,	121,	'2011-07-21 05:38:59',	NULL,	'INSERT',	'Tijeras'),
(230,	122,	'2011-07-21 05:38:59',	NULL,	'INSERT',	'Tijeras'),
(231,	118,	'2011-07-21 05:41:48',	NULL,	'DELETE',	''),
(232,	119,	'2011-07-21 05:41:48',	NULL,	'DELETE',	''),
(233,	120,	'2011-07-21 05:41:48',	NULL,	'DELETE',	''),
(234,	121,	'2011-07-21 05:41:48',	NULL,	'DELETE',	''),
(235,	122,	'2011-07-21 05:41:48',	NULL,	'DELETE',	''),
(236,	123,	'2011-07-21 05:55:36',	NULL,	'INSERT',	'Tijeras'),
(237,	124,	'2011-07-21 05:55:36',	NULL,	'INSERT',	'Tijeras'),
(238,	125,	'2011-07-21 05:55:37',	NULL,	'INSERT',	'Tijeras'),
(239,	126,	'2011-07-21 05:55:37',	NULL,	'INSERT',	'Tijeras'),
(240,	127,	'2011-07-21 05:55:37',	NULL,	'INSERT',	'Tijeras'),
(241,	123,	'2011-07-21 05:55:43',	NULL,	'DELETE',	''),
(242,	124,	'2011-07-21 05:55:43',	NULL,	'DELETE',	''),
(243,	125,	'2011-07-21 05:55:43',	NULL,	'DELETE',	''),
(244,	126,	'2011-07-21 05:55:43',	NULL,	'DELETE',	''),
(245,	127,	'2011-07-21 05:55:43',	NULL,	'DELETE',	''),
(246,	128,	'2011-07-21 05:59:05',	NULL,	'INSERT',	'Tijeras'),
(247,	129,	'2011-07-21 05:59:05',	NULL,	'INSERT',	'Tijeras'),
(248,	130,	'2011-07-21 05:59:05',	NULL,	'INSERT',	'Tijeras'),
(249,	131,	'2011-07-21 05:59:05',	NULL,	'INSERT',	'Tijeras'),
(250,	132,	'2011-07-21 05:59:05',	NULL,	'INSERT',	'Tijeras'),
(251,	128,	'2011-07-21 05:59:09',	NULL,	'DELETE',	''),
(252,	129,	'2011-07-21 05:59:09',	NULL,	'DELETE',	''),
(253,	130,	'2011-07-21 05:59:09',	NULL,	'DELETE',	''),
(254,	131,	'2011-07-21 05:59:09',	NULL,	'DELETE',	''),
(255,	132,	'2011-07-21 05:59:09',	NULL,	'DELETE',	''),
(256,	133,	'2011-07-21 05:59:28',	NULL,	'INSERT',	'POPO'),
(257,	134,	'2011-07-21 05:59:28',	NULL,	'INSERT',	'POPO'),
(258,	135,	'2011-07-21 05:59:28',	NULL,	'INSERT',	'POPO'),
(259,	136,	'2011-07-21 05:59:28',	NULL,	'INSERT',	'POPO'),
(260,	137,	'2011-07-21 05:59:28',	NULL,	'INSERT',	'POPO'),
(261,	133,	'2011-07-21 05:59:36',	NULL,	'DELETE',	''),
(262,	134,	'2011-07-21 05:59:36',	NULL,	'DELETE',	''),
(263,	135,	'2011-07-21 05:59:36',	NULL,	'DELETE',	''),
(264,	136,	'2011-07-21 05:59:36',	NULL,	'DELETE',	''),
(265,	137,	'2011-07-21 05:59:36',	NULL,	'DELETE',	''),
(266,	24,	'2011-07-21 07:16:06',	NULL,	'DELETE',	''),
(267,	25,	'2011-07-21 07:16:06',	NULL,	'DELETE',	''),
(268,	26,	'2011-07-21 07:16:06',	NULL,	'DELETE',	''),
(269,	138,	'2011-07-21 15:35:46',	NULL,	'INSERT',	''),
(270,	139,	'2011-07-21 15:35:46',	NULL,	'INSERT',	''),
(271,	140,	'2011-07-21 15:35:46',	NULL,	'INSERT',	''),
(272,	141,	'2011-07-21 15:35:46',	NULL,	'INSERT',	''),
(273,	142,	'2011-07-21 15:35:46',	NULL,	'INSERT',	''),
(274,	143,	'2011-07-21 15:35:46',	NULL,	'INSERT',	''),
(275,	144,	'2011-07-21 15:35:46',	NULL,	'INSERT',	''),
(276,	145,	'2011-07-21 15:35:46',	NULL,	'INSERT',	''),
(277,	146,	'2011-07-21 15:35:46',	NULL,	'INSERT',	''),
(278,	147,	'2011-07-21 15:35:47',	NULL,	'INSERT',	''),
(279,	148,	'2011-07-21 15:35:47',	NULL,	'INSERT',	''),
(280,	149,	'2011-07-21 15:35:47',	NULL,	'INSERT',	''),
(281,	150,	'2011-07-21 15:35:47',	NULL,	'INSERT',	''),
(282,	151,	'2011-07-21 15:35:47',	NULL,	'INSERT',	''),
(283,	152,	'2011-07-21 15:35:47',	NULL,	'INSERT',	''),
(284,	153,	'2011-07-21 15:35:47',	NULL,	'INSERT',	''),
(285,	154,	'2011-07-21 15:35:47',	NULL,	'INSERT',	''),
(286,	155,	'2011-07-21 15:35:47',	NULL,	'INSERT',	''),
(287,	156,	'2011-07-21 15:35:47',	NULL,	'INSERT',	''),
(288,	157,	'2011-07-21 15:35:48',	NULL,	'INSERT',	''),
(289,	47,	'2011-07-21 15:38:29',	NULL,	'DELETE',	''),
(290,	48,	'2011-07-21 15:38:29',	NULL,	'DELETE',	''),
(291,	49,	'2011-07-21 15:38:29',	NULL,	'DELETE',	''),
(292,	50,	'2011-07-21 15:38:29',	NULL,	'DELETE',	''),
(293,	51,	'2011-07-21 15:38:29',	NULL,	'DELETE',	''),
(294,	52,	'2011-07-21 15:38:29',	NULL,	'DELETE',	''),
(295,	53,	'2011-07-21 15:38:29',	NULL,	'DELETE',	''),
(296,	54,	'2011-07-21 15:38:29',	NULL,	'DELETE',	''),
(297,	55,	'2011-07-21 15:38:30',	NULL,	'DELETE',	''),
(298,	10,	'2011-07-21 15:41:30',	NULL,	'UPDATE: Estado Limpieza->Disponible\nUPDATE: Ubicacion Sala 2->Sala 1\n',	''),
(299,	10,	'2011-07-21 15:42:13',	NULL,	'DELETE',	'');

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

INSERT INTO `Historial_Paquetes` (`idHistorialPaquete`, `idPaquete`, `idEquipo`, `idInstrumento`, `fechaCambio`, `idUsuario`, `tipoOperacion`, `campo`, `valorAnterior`, `valorNuevo`, `observaciones`, `nombrePaquetePrevio`) VALUES
(1,	1,	NULL,	NULL,	'2025-05-25 20:44:19',	NULL,	'INSERT',	NULL,	NULL,	NULL,	'Nuevo paquete creado',	''),
(2,	2,	NULL,	NULL,	'2025-05-26 01:52:08',	NULL,	'INSERT',	NULL,	NULL,	NULL,	'Nuevo paquete creado',	''),
(3,	2,	NULL,	NULL,	'2025-05-26 01:55:45',	NULL,	'DELETE',	NULL,	NULL,	NULL,	'Paquete eliminado',	''),
(4,	3,	NULL,	NULL,	'2025-05-26 01:56:22',	NULL,	'INSERT',	NULL,	NULL,	NULL,	'Nuevo paquete creado',	''),
(5,	1,	NULL,	NULL,	'2025-05-26 02:54:11',	NULL,	'UPDATE',	'idEspecialidad',	'2',	'12',	'Cambio de idEspecialidad: 2 -> 12',	''),
(6,	1,	NULL,	NULL,	'2025-05-26 12:00:43',	NULL,	'UPDATE',	'idEspecialidad',	'12',	'2',	'Cambio de idEspecialidad: 12 -> 2',	''),
(7,	4,	NULL,	NULL,	'2025-05-29 00:58:54',	NULL,	'INSERT',	NULL,	NULL,	NULL,	'Nuevo paquete creado',	''),
(8,	5,	NULL,	NULL,	'2025-05-29 18:21:56',	NULL,	'INSERT',	NULL,	NULL,	NULL,	'Nuevo paquete creado',	''),
(9,	5,	NULL,	NULL,	'2025-05-29 18:22:19',	NULL,	'DELETE',	NULL,	NULL,	NULL,	'Paquete eliminado',	''),
(10,	6,	NULL,	NULL,	'2025-05-29 18:22:36',	NULL,	'INSERT',	NULL,	NULL,	NULL,	'Nuevo paquete creado',	''),
(11,	6,	NULL,	NULL,	'2025-05-29 18:23:11',	NULL,	'DELETE',	NULL,	NULL,	NULL,	'Paquete eliminado',	''),
(12,	7,	NULL,	NULL,	'2025-05-29 18:23:25',	NULL,	'INSERT',	NULL,	NULL,	NULL,	'Nuevo paquete creado',	''),
(13,	7,	NULL,	NULL,	'2025-05-29 18:25:27',	NULL,	'DELETE',	NULL,	NULL,	NULL,	'Paquete eliminado',	''),
(14,	8,	NULL,	NULL,	'2025-05-29 18:25:45',	NULL,	'INSERT',	NULL,	NULL,	NULL,	'Nuevo paquete creado',	''),
(15,	8,	NULL,	NULL,	'2025-05-29 18:26:01',	NULL,	'DELETE',	NULL,	NULL,	NULL,	'Paquete eliminado',	''),
(16,	9,	NULL,	NULL,	'2025-05-29 18:26:14',	NULL,	'INSERT',	NULL,	NULL,	NULL,	'Nuevo paquete creado',	''),
(17,	9,	NULL,	NULL,	'2025-05-29 18:30:41',	NULL,	'DELETE',	NULL,	NULL,	NULL,	'Paquete eliminado',	''),
(18,	10,	NULL,	NULL,	'2025-05-29 18:30:58',	NULL,	'INSERT',	NULL,	NULL,	NULL,	'Nuevo paquete creado',	''),
(19,	10,	NULL,	NULL,	'2025-05-29 18:32:06',	NULL,	'DELETE',	NULL,	NULL,	NULL,	'Paquete eliminado',	''),
(20,	11,	NULL,	NULL,	'2025-05-29 18:32:19',	NULL,	'INSERT',	NULL,	NULL,	NULL,	'Nuevo paquete creado',	''),
(21,	11,	NULL,	NULL,	'2025-05-29 18:48:54',	NULL,	'DELETE',	NULL,	NULL,	NULL,	'Paquete eliminado',	''),
(22,	12,	NULL,	NULL,	'2025-05-29 18:49:05',	NULL,	'INSERT',	NULL,	NULL,	NULL,	'Nuevo paquete creado',	''),
(23,	12,	1,	NULL,	'2025-05-29 18:49:07',	NULL,	'INSERT',	NULL,	NULL,	NULL,	'Equipo agregado al paquete',	''),
(24,	1,	NULL,	1,	'2011-07-21 02:29:28',	NULL,	'INSERT',	NULL,	NULL,	NULL,	'Instrumento agregado al paquete',	''),
(25,	1,	NULL,	1,	'2011-07-21 02:29:44',	NULL,	'DELETE',	NULL,	NULL,	NULL,	'Instrumento removido del paquete',	''),
(26,	1,	NULL,	1,	'2011-07-21 02:30:09',	NULL,	'DELETE',	NULL,	NULL,	NULL,	'Instrumento removido del paquete',	''),
(27,	12,	NULL,	5,	'2011-07-21 03:23:32',	NULL,	'INSERT',	NULL,	NULL,	NULL,	'Instrumento agregado al paquete',	''),
(28,	12,	NULL,	5,	'2011-07-21 03:26:09',	NULL,	'DELETE',	NULL,	NULL,	NULL,	'Instrumento removido del paquete',	''),
(29,	12,	9,	NULL,	'2011-07-21 03:28:08',	NULL,	'INSERT',	NULL,	NULL,	NULL,	'Equipo agregado al paquete',	''),
(30,	13,	NULL,	NULL,	'2011-07-21 07:28:09',	NULL,	'INSERT',	NULL,	NULL,	NULL,	'Nuevo paquete creado',	'PRUEBA 1'),
(31,	13,	NULL,	NULL,	'2011-07-21 07:28:36',	NULL,	'DELETE',	NULL,	NULL,	NULL,	'Paquete eliminado',	''),
(32,	14,	NULL,	NULL,	'2011-07-21 07:34:50',	NULL,	'INSERT',	NULL,	NULL,	NULL,	'Nuevo paquete creado',	''),
(33,	1,	NULL,	5,	'2011-07-21 09:29:48',	NULL,	'INSERT',	NULL,	NULL,	NULL,	'Instrumento agregado al paquete',	''),
(34,	1,	9,	NULL,	'2011-07-21 11:11:37',	NULL,	'INSERT',	NULL,	NULL,	NULL,	'Equipo agregado al paquete',	''),
(35,	14,	9,	NULL,	'2011-07-21 11:11:55',	NULL,	'INSERT',	NULL,	NULL,	NULL,	'Equipo agregado al paquete',	''),
(36,	1,	NULL,	5,	'2011-07-21 15:41:29',	NULL,	'UPDATE',	'cantidad',	'9',	'10',	'Cantidad modificada: 9 -> 10',	''),
(37,	1,	NULL,	5,	'2011-07-21 15:41:42',	NULL,	'UPDATE',	'cantidad',	'10',	'9',	'Cantidad modificada: 10 -> 9',	''),
(38,	14,	NULL,	26,	'2011-07-21 16:11:23',	NULL,	'INSERT',	NULL,	NULL,	NULL,	'Instrumento agregado al paquete',	''),
(39,	14,	NULL,	26,	'2011-07-21 16:45:20',	NULL,	'UPDATE',	'cantidad',	'2',	'3',	'Cantidad modificada: 2 -> 3',	''),
(40,	14,	NULL,	26,	'2011-07-21 16:51:24',	NULL,	'UPDATE',	'cantidad',	'3',	'2',	'Cantidad modificada: 3 -> 2',	''),
(41,	14,	NULL,	26,	'2011-07-21 16:51:35',	NULL,	'UPDATE',	'cantidad',	'2',	'4',	'Cantidad modificada: 2 -> 4',	'');

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

INSERT INTO `Historial_Pedido` (`idHistorialPedido`, `idPedido`, `EstadoAnterior`, `EstadoNuevo`, `FechaCambio`, `idUsuario`) VALUES
(1,	2,	NULL,	'Pedido',	'2025-05-25 20:44:45',	NULL),
(2,	2,	'Pedido',	'Aprobado',	'2025-05-26 00:24:34',	NULL),
(3,	2,	'Aprobado',	'Entregado',	'2025-05-26 00:25:13',	NULL),
(4,	2,	'Entregado',	'Finalizado',	'2025-05-26 00:27:44',	NULL),
(5,	2,	'Finalizado',	'Pedido',	'2025-05-26 00:40:18',	NULL),
(6,	12,	NULL,	'Pedido',	'2025-05-26 00:48:16',	NULL),
(7,	13,	NULL,	'Pedido',	'2025-05-26 00:48:56',	NULL),
(8,	12,	'Pedido',	'',	'2025-05-26 00:53:59',	NULL),
(9,	13,	'Pedido',	'',	'2025-05-26 00:54:31',	NULL),
(10,	14,	NULL,	'',	'2025-05-26 01:01:09',	NULL),
(11,	14,	'',	'',	'2025-05-26 01:28:22',	NULL),
(12,	15,	NULL,	'Pedido',	'2025-05-26 01:32:07',	NULL),
(13,	15,	'Pedido',	'Aprobado',	'2025-05-26 01:34:34',	NULL),
(14,	16,	NULL,	'Pedido',	'2025-05-28 23:25:24',	NULL),
(15,	16,	'Pedido',	'Aprobado',	'2025-05-28 23:25:55',	NULL),
(16,	17,	NULL,	'Pedido',	'2025-05-29 01:42:00',	NULL),
(17,	17,	'Pedido',	'',	'2025-05-29 17:56:13',	NULL),
(18,	16,	'Aprobado',	'',	'2025-05-29 17:56:24',	NULL);

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

INSERT INTO `IInstrumento` (`idInstrumentoIndividual`, `ultimaEsterilizacion`, `Estado`, `Ubicacion`, `idInstrumentoGrupo`, `idEquipo`, `idPaquete`) VALUES
(3,	'2025-05-22 18:22:39',	'En Uso',	'Almacen',	2,	NULL,	NULL),
(4,	'2025-06-07 00:00:00',	'Limpieza',	'Almacen',	3,	NULL,	NULL),
(5,	'2025-05-26 15:26:34',	'Pendiente',	'Almacen',	3,	NULL,	NULL),
(6,	'2025-05-26 15:26:34',	'Disponible',	'Almacen',	3,	NULL,	NULL),
(7,	'2025-07-30 14:30:00',	'Disponible',	'Sala 1',	3,	NULL,	NULL),
(8,	'2025-05-31 00:00:00',	'Disponible',	'Sala 1',	4,	NULL,	NULL),
(9,	'2025-05-22 00:00:00',	'En Uso',	'Sala 1',	4,	NULL,	NULL),
(12,	'2025-05-26 15:36:54',	'Disponible',	'Almacen',	6,	NULL,	NULL),
(13,	'2025-05-26 15:36:54',	'Disponible',	'Almacen',	6,	NULL,	NULL),
(14,	'2025-05-26 15:36:54',	'Disponible',	'Almacen',	6,	NULL,	NULL),
(56,	'2011-07-21 02:21:40',	'Disponible',	'Almacen',	6,	NULL,	NULL),
(57,	'2011-07-21 02:21:40',	'Disponible',	'Almacen',	6,	NULL,	NULL),
(58,	'2011-07-21 02:21:40',	'Disponible',	'Almacen',	6,	NULL,	NULL),
(59,	'2011-07-21 02:21:40',	'Disponible',	'Almacen',	6,	NULL,	NULL),
(60,	'2011-07-21 02:21:40',	'Disponible',	'Almacen',	6,	NULL,	NULL),
(61,	'2011-07-21 02:21:40',	'Disponible',	'Almacen',	6,	NULL,	NULL),
(62,	'2011-07-21 02:21:40',	'Disponible',	'Almacen',	6,	NULL,	NULL),
(138,	'2011-07-21 15:35:46',	'Disponible',	'Almacen',	26,	12,	NULL),
(139,	'2011-07-21 15:35:46',	'Disponible',	'Almacen',	26,	12,	NULL),
(140,	'2011-07-21 15:35:46',	'Disponible',	'Almacen',	26,	NULL,	14),
(141,	'2011-07-21 15:35:46',	'Disponible',	'Almacen',	26,	NULL,	14),
(142,	'2011-07-21 15:35:46',	'Disponible',	'Almacen',	26,	NULL,	14),
(143,	'2011-07-21 15:35:46',	'Disponible',	'Almacen',	26,	NULL,	14),
(144,	'2011-07-21 15:35:46',	'Disponible',	'Almacen',	26,	NULL,	NULL),
(145,	'2011-07-21 15:35:46',	'Disponible',	'Almacen',	26,	NULL,	NULL),
(146,	'2011-07-21 15:35:46',	'Disponible',	'Almacen',	26,	NULL,	NULL),
(147,	'2011-07-21 15:35:47',	'Disponible',	'Almacen',	26,	NULL,	NULL),
(148,	'2011-07-21 15:35:47',	'Disponible',	'Almacen',	26,	NULL,	NULL),
(149,	'2011-07-21 15:35:47',	'Disponible',	'Almacen',	26,	NULL,	NULL),
(150,	'2011-07-21 15:35:47',	'Disponible',	'Almacen',	26,	NULL,	NULL),
(151,	'2011-07-21 15:35:47',	'Disponible',	'Almacen',	26,	NULL,	NULL),
(152,	'2011-07-21 15:35:47',	'Disponible',	'Almacen',	26,	NULL,	NULL),
(153,	'2011-07-21 15:35:47',	'Disponible',	'Almacen',	26,	NULL,	NULL),
(154,	'2011-07-21 15:35:47',	'Disponible',	'Almacen',	26,	NULL,	NULL),
(155,	'2011-07-21 15:35:47',	'Disponible',	'Almacen',	26,	NULL,	NULL),
(156,	'2011-07-21 15:35:47',	'Disponible',	'Almacen',	26,	9,	NULL),
(157,	'2011-07-21 15:35:48',	'Disponible',	'Almacen',	26,	9,	NULL);

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

INSERT INTO `Paquete` (`idPaquete`, `Nombre`, `idEspecialidad`) VALUES
(1,	'Paquete de Cirugia General',	2),
(3,	'Paquete de Cuidados',	8),
(12,	'Paquete',	7),
(14,	'PRUEBA 1',	2);

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

INSERT INTO `Paquete_Equipo` (`idPaquete`, `idEquipo`) VALUES
(12,	1),
(1,	9),
(12,	9),
(14,	9);

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

INSERT INTO `Paquete_Instrumento` (`idPaquete`, `idInstrumento`, `cantidad`) VALUES
(1,	5,	9),
(14,	26,	4);

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

INSERT INTO `Pedido` (`idPedido`, `Fecha`, `Hora`, `Ubicacion`, `Cirugia`, `Estado`, `idEnfermero`, `idPaquete`) VALUES
(2,	'2025-05-26',	'11:00:00',	'Almacen',	'Cirugia General',	'Pedido',	12,	1),
(15,	'2025-05-27',	'11:32:00',	'Sala 1',	'Cirugia Pediatrica',	'Aprobado',	12,	1);

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

INSERT INTO `Pedido_Equipo` (`idPedido`, `idEquipo`) VALUES
(2,	9);

DROP TABLE IF EXISTS `Pedido_IInstrumento`;
CREATE TABLE `Pedido_IInstrumento` (
  `idPedido` int(11) NOT NULL,
  `idInstrumento` int(11) NOT NULL,
  PRIMARY KEY (`idPedido`,`idInstrumento`),
  CONSTRAINT `FK_PedidoGInstrumento_GInstrumento` FOREIGN KEY (`idPedido`) REFERENCES `Pedido` (`idpedido`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

INSERT INTO `Pedido_IInstrumento` (`idPedido`, `idInstrumento`) VALUES
(2,	4),
(2,	6),
(2,	8),
(2,	9),
(2,	10),
(15,	49);

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

INSERT INTO `Usuario` (`idUsuario`, `Nombres`, `ApellidoPaterno`, `ApellidoMaterno`, `Rol`, `Alias`, `Correo`, `Contrasena`) VALUES
(1,	'Oscar Alejandro',	'Becerra',	'Cervantes',	'Administrador',	NULL,	'becerra.oscar@uabc.edu.mx',	'1caf3ebede08d1c54febd9be5629e98882bc0f572bf633df8aaed92feb9d5814'),
(10,	'Rosselin',	'Gil',	'Soto',	'Enfermero',	'Enfermero',	'ross@ross.com',	'Alias chido'),
(12,	'Sammuel Roberto',	'Perez',	'Hernandez',	'Enfermero',	NULL,	'sammy@sammy.com',	'aaf5ad63ac417e5002bdac202e07287cf90f35b1d419464d2c4fc79e508a1e4c'),
(13,	'Pablo Yair',	'Rosas',	'Ibarraran',	'Almacenista',	NULL,	'pablo@pablo.com',	'26079e41910bcde04be636fbeecc9045379882b5ad3fe7f70b762436c6d98055'),
(15,	'PANCHO',	'Pérez',	'Gómez',	'Enfermero',	'PAPA',	'juan.perez@example.com',	'b221d9dbb083a7f33428d7c2a3c3198ae925614d70210e28716ccaa7cd4ddb79');

-- 2011-09-05 21:23:38
