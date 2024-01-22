-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Tiempo de generación: 22-01-2024 a las 17:00:16
-- Versión del servidor: 8.2.0
-- Versión de PHP: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Base de datos: `aleobot`
--

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `accounts`
--

CREATE TABLE `accounts` (
  `broker_id` int UNSIGNED NOT NULL,
  `nroComitente` int UNSIGNED NOT NULL,
  `dni` int UNSIGNED NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Estructura Stand-in para la vista `accounts_view`
-- (Véase abajo para la vista actual)
--
CREATE TABLE `accounts_view` (
`nroComitente` int unsigned
,`broker_id` int unsigned
,`broker` varchar(255)
,`dni` int unsigned
,`nombreCompleto` varchar(255)
);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `brokers`
--

CREATE TABLE `brokers` (
  `id` int(3) UNSIGNED ZEROFILL NOT NULL,
  `nombre` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `short_str` char(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `credentials`
--

CREATE TABLE `credentials` (
  `broker_id` int UNSIGNED NOT NULL,
  `nroComitente` int UNSIGNED NOT NULL,
  `module` varchar(16) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `user` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT '',
  `password` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `conn_id` smallint UNSIGNED NOT NULL,
  `conn_token` varchar(999) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT ''
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Estructura Stand-in para la vista `credentials_view`
-- (Véase abajo para la vista actual)
--
CREATE TABLE `credentials_view` (
`nroComitente` int unsigned
,`nombreCompleto` varchar(255)
,`broker_id` int unsigned
,`broker` varchar(255)
,`module` varchar(16)
,`user` varchar(30)
,`password` varchar(255)
,`conn_id` smallint unsigned
,`conn_token` varchar(999)
);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `modules`
--

CREATE TABLE `modules` (
  `name` varchar(16) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `orders`
--

CREATE TABLE `orders` (
  `id` int UNSIGNED NOT NULL,
  `conn_id` char(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `id_ext` char(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `instrument` char(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '(str_id)',
  `settlement` tinyint UNSIGNED NOT NULL COMMENT '(int_id)',
  `op_type` tinyint NOT NULL COMMENT '(int_id)',
  `size` mediumint UNSIGNED NOT NULL,
  `price` float UNSIGNED NOT NULL,
  `remaining` mediumint UNSIGNED NOT NULL,
  `status` tinyint UNSIGNED NOT NULL COMMENT '(int_id)',
  `currency` tinyint UNSIGNED NOT NULL COMMENT '(int_id)',
  `amount` tinyint UNSIGNED NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `persons`
--

CREATE TABLE `persons` (
  `dni` int UNSIGNED NOT NULL,
  `nombreCompleto` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `CUIT` bigint UNSIGNED NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `settlements`
--

CREATE TABLE `settlements` (
  `t` tinyint UNSIGNED NOT NULL,
  `str1` char(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `str2` char(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Estructura para la vista `accounts_view`
--
DROP TABLE IF EXISTS `accounts_view`;

CREATE ALGORITHM=UNDEFINED DEFINER=`ale`@`%` SQL SECURITY DEFINER VIEW `accounts_view`  AS SELECT `a`.`nroComitente` AS `nroComitente`, `a`.`broker_id` AS `broker_id`, `b`.`nombre` AS `broker`, `a`.`dni` AS `dni`, `p`.`nombreCompleto` AS `nombreCompleto` FROM ((`accounts` `a` join `persons` `p` on((`a`.`dni` = `p`.`dni`))) join `brokers` `b` on((`a`.`broker_id` = `b`.`id`)))WITH CASCADED CHECK OPTION  ;

-- --------------------------------------------------------

--
-- Estructura para la vista `credentials_view`
--
DROP TABLE IF EXISTS `credentials_view`;

CREATE ALGORITHM=UNDEFINED DEFINER=`ale`@`%` SQL SECURITY DEFINER VIEW `credentials_view`  AS SELECT `crd`.`nroComitente` AS `nroComitente`, `prs`.`nombreCompleto` AS `nombreCompleto`, `crd`.`broker_id` AS `broker_id`, `brk`.`nombre` AS `broker`, `crd`.`module` AS `module`, `crd`.`user` AS `user`, `crd`.`password` AS `password`, `crd`.`conn_id` AS `conn_id`, `crd`.`conn_token` AS `conn_token` FROM (((`credentials` `crd` join `accounts` `acct` on(((`crd`.`broker_id` = `acct`.`broker_id`) and (`crd`.`nroComitente` = `acct`.`nroComitente`)))) join `persons` `prs` on((`acct`.`dni` = `prs`.`dni`))) join `brokers` `brk` on((`crd`.`broker_id` = `brk`.`id`))) ;

--
-- Índices para tablas volcadas
--

--
-- Indices de la tabla `accounts`
--
ALTER TABLE `accounts`
  ADD PRIMARY KEY (`broker_id`,`nroComitente`),
  ADD KEY `dni` (`dni`);

--
-- Indices de la tabla `brokers`
--
ALTER TABLE `brokers`
  ADD PRIMARY KEY (`id`);

--
-- Indices de la tabla `credentials`
--
ALTER TABLE `credentials`
  ADD PRIMARY KEY (`broker_id`,`nroComitente`,`module`),
  ADD KEY `module` (`module`),
  ADD KEY `conn_id` (`conn_id`);

--
-- Indices de la tabla `modules`
--
ALTER TABLE `modules`
  ADD PRIMARY KEY (`name`);

--
-- Indices de la tabla `orders`
--
ALTER TABLE `orders`
  ADD PRIMARY KEY (`id`),
  ADD KEY `idx_id_ext` (`id_ext`);

--
-- Indices de la tabla `persons`
--
ALTER TABLE `persons`
  ADD PRIMARY KEY (`dni`);

--
-- Indices de la tabla `settlements`
--
ALTER TABLE `settlements`
  ADD PRIMARY KEY (`t`);

--
-- AUTO_INCREMENT de las tablas volcadas
--

--
-- AUTO_INCREMENT de la tabla `credentials`
--
ALTER TABLE `credentials`
  MODIFY `conn_id` smallint UNSIGNED NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `orders`
--
ALTER TABLE `orders`
  MODIFY `id` int UNSIGNED NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `settlements`
--
ALTER TABLE `settlements`
  MODIFY `t` tinyint UNSIGNED NOT NULL AUTO_INCREMENT;

--
-- Restricciones para tablas volcadas
--

--
-- Filtros para la tabla `accounts`
--
ALTER TABLE `accounts`
  ADD CONSTRAINT `accounts_ibfk_1` FOREIGN KEY (`broker_id`) REFERENCES `brokers` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `accounts_ibfk_2` FOREIGN KEY (`dni`) REFERENCES `persons` (`dni`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Filtros para la tabla `credentials`
--
ALTER TABLE `credentials`
  ADD CONSTRAINT `credentials_ibfk_1` FOREIGN KEY (`broker_id`,`nroComitente`) REFERENCES `accounts` (`broker_id`, `nroComitente`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `credentials_ibfk_2` FOREIGN KEY (`module`) REFERENCES `modules` (`name`) ON DELETE CASCADE ON UPDATE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
