--- This file is part of LinkyRPi.
--- LinkyRPi is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
--- LinkyRPi is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
--- You should have received a copy of the GNU General Public License along with LinkyRPi. If not, see <https://www.gnu.org/licenses/>.
--- (c)Copyright Mikaël Masci 2022

--------------------------------------------------------------------------------------
--- CREATION DE LA BASE DE DONNEES                                                 ---
--------------------------------------------------------------------------------------
DROP DATABASE Linky;
CREATE DATABASE linkydb WITH
  OWNER =  Linky
  ENCODING = 'UTF8'
  TABLESPACE = pg_default
  CONNECTION LIMIT = -1;

COMMENT ON DATABASE linkydb IS 'Database for LinkyRPi';

--------------------------------------------------------------------------------------
--- CREATION DL4EXTENSION PERMETTANT DE CREER DES UUID V4                          ---
--------------------------------------------------------------------------------------
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";


--------------------------------------------------------------------------------------
--- CREATION DES TABLES                                                            ---
--------------------------------------------------------------------------------------
CREATE TABLE Compteur (
  AdresseCompteur char(12) NOT NULL PRIMARY KEY,
  PRM	            char(14),
  TypeCompteur    char(10) NOT NULL,
  NomCompteur     varchar(200),
  VersionTIC      char(2),
  CONSTRAINT Ccompteur UNIQUE(AdresseCompteur)
);

CREATE TABLE Abonnement (
  AbonnementId        uuid DEFAULT uuid_generate_v4 () NOT NULL PRIMARY KEY,
  AdresseCompteur     char(12),
  TarifSouscrit       varchar(50),
  HorairesHC          varchar(100),
  IntensiteSouscrite  int,
  PuissanceCoupure    int,
  DateCre             TIMESTAMP,
  DateClos            TIMESTAMP,
  Status              char(4)
);

CREATE TABLE Mesures (
  AbonnementId	                             uuid NOT NULL,
  DateHeureLinky                             TIMESTAMP NOT NULL DEFAULT NOW(),
  DepassementPuissance                       int,
  DepassementPuissancePhase1                 int,
  DepassementPuissancePhase2                 int,
  DepassementPuissancePhase3                 int,
  PuissanceApparente                         int,
  PuissanceApparentePhase1                   int,
  PuissanceApparentePhase2                   int,
  PuissanceApparentePhase3                   int,
  PuissanceMaxAtteinte                       int,
  PuissanceMaxAtteintePhase1                 int,
  PuissanceMaxAtteintePhase2                 int,
  PuissanceMaxAtteintePhase3                 int,
  PuissanceApparenteMaxN1                    int,
  PuissanceApparenteMaxN1Phase1              int,
  PuissanceApparenteMaxN1Phase2              int,
  PuissanceApparenteMaxN1Phase3              int,
  PointNCourbeChargeActiveSoutiree           int,
  PointN1CourbeChargeActiveSoutiree          int,
  IndexBase                                  float,
  IndexTotal                                 float,
  IndexHC	                                   float,
  IndexHP	                                   float,
  IndexWE	                                   float,
  IndexHCSaisonHaute	                       float,
  IndexHPSaisonHaute	                       float,
  IndexHCSaisonBasse	                       float,
  IndexHPSaisonBasse	                       float,
  IndexEJPNormale	                           float,
  IndexEJPPointe                             float,
  IndexHCJB	                                 float,
  IndexHCJW	                                 float,
  IndexHCJR         	                       float,
  IndexHPJB	                                 float,
  IndexHPJW	                                 float,
  IndexHPJR         	                       float,
  Index07	                                   float,
  Index08	                                   float,
  Index09	                                   float,
  Index10	                                   float,
  EnergieActiveSoutireeDistributeurIndex1    float,
  EnergieActiveSoutireeDistributeurIndex2    float,
  EnergieActiveSoutireeDistributeurIndex3    float,
  EnergieActiveSoutireeDistributeurIndex4    float,
  TensionEfficacePhase1                      int,
  TensionEfficacePhase2                      int,
  TensionEfficacePhase3                      int,
  TensionMoyennePhase1                       int,
  TensionMoyennePhase2                       int,
  TensionMoyennePhase3                       int,
  IntensiteInstantanee                       int,
  IntensiteInstantaneePhase1                 int,
  IntensiteInstantaneePhase2                 int,
  IntensiteInstantaneePhase3                 int,
  IntensiteMax                               int,
  IntensiteMaxPhase1                         int,
  IntensiteMaxPhase2                         int,
  IntensiteMaxPhase3                         int,
  ContactSec                              varchar(6),
  OrganeDeCoupure                         varchar(100),
  CacheBorneDistributeur                  varchar(6),
  SurtensionPhase                         char(3),
  DepassementPuissanceRef                 char(3),
  Fonctionnement                          varchar(12),
  SensEnergieActive                       varchar(8),
  TarifEnCoursF                           varchar(30),
  TarifEnCoursD                           varchar(30),
  HorlogeDegradee                         varchar(30),
  SortieCommEuridis                       varchar(30),
  StatutCPL                               varchar(20),
  SynchroCPL                              varchar(15),
  CouleurTempoJour                        varchar(20),
  CouleurTempoDemain                      varchar(20),
  PreavisPointesMobiles                   varchar(25),
  PointeMobile                            varchar(20),
  ModeTIC                                 varchar(10),
  PeriodeTarifaireEnCours                 char(4),
  MotEtat                                 char(6),
  NumeroJourCalendrierFournisseur         char(2),
  NumeroProchainJourCalendrierFournisseur char(2),
  ProfilProchainJourCalendrierFournisseur varchar(100),
  ProfilProchainJourPointe                varchar(100),
  PresenceDesPotentiels                   char(2),
  MessageCourt                            varchar(32),
  MessageUltraCourt                       varchar(16),
  DebutPointeMobile1                      char(2),
  FinPointeMobile1                        char(2),
  DebutPointeMobile2                      char(2),
  FinPointeMobile2                        char(2),
  DebutPointeMobile3                      char(2),
  FinPointeMobile3                        char(2),
  Relais1	                                boolean,
  Relais2	                                boolean,
  Relais3	                                boolean,
  Relais4	                                boolean,
  Relais5	                                boolean,
  Relais6	                                boolean,
  Relais7	                                boolean,
  Relais8	                                boolean
);

--------------------------------------------------------------------------------------
--- CREATION DES AUTORISATIONS                                                     ---
--------------------------------------------------------------------------------------
-- Read/write role
CREATE ROLE LinkyRW;
GRANT CONNECT ON DATABASE linkydb TO LinkyRW;
GRANT ALL ON TABLE public.abonnement TO linkyrw;
GRANT ALL ON TABLE public.compteur TO linkyrw;
GRANT ALL ON TABLE public.mesures TO linkyrw;

-- Users creation
CREATE USER linky WITH PASSWORD 'linky2Rpi';

-- Grant privileges to users
GRANT LinkyRW TO linky;
