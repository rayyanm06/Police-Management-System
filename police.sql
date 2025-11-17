DROP DATABASE IF EXISTS police;
CREATE DATABASE police;
USE police;

--------------------------------------------------------
-- 1. Department Table
--------------------------------------------------------
CREATE TABLE Department (  
    Dept_ID INT PRIMARY KEY,  
    DepartmentType VARCHAR(100) UNIQUE NOT NULL,  
    DepartmentHead VARCHAR(100) UNIQUE NOT NULL,  
    PhoneNumber CHAR(10) UNIQUE NOT NULL,  
    Email CHAR(100) NOT NULL UNIQUE CHECK (Email LIKE '%@%'),  
    EstablishedDate DATE  
);

--------------------------------------------------------
-- 2. Police Table (Before Station)
--------------------------------------------------------
CREATE TABLE Police(  
    PoliceID INT PRIMARY KEY AUTO_INCREMENT,  
    PoliceName VARCHAR(100) NOT NULL,  
    Ranking CHAR(100),  
    Email VARCHAR(100) NOT NULL UNIQUE CHECK (Email LIKE '%@%'),  
    PhoneNumber CHAR(10),  
    Date_of_Birth DATE,  
    Age INT NOT NULL CHECK(Age >= 18 AND Age <= 55),  
    Dept_ID INT,
    Salary DECIMAL(8,2),
    FOREIGN KEY (Dept_ID) REFERENCES Department(Dept_ID)
);

--------------------------------------------------------
-- 3. Station Table
--------------------------------------------------------
CREATE TABLE Station (
    Station_ID INT PRIMARY KEY AUTO_INCREMENT,
    StationName VARCHAR(100) UNIQUE NOT NULL,
    Location VARCHAR(150),
    ContactNumber CHAR(10) UNIQUE,
    InChargeOfficer_ID INT,
    Dept_ID INT,
    FOREIGN KEY (Dept_ID) REFERENCES Department(Dept_ID),
    FOREIGN KEY (InChargeOfficer_ID) REFERENCES Police(PoliceID)
);

--------------------------------------------------------
-- 4. CaseTable
--------------------------------------------------------
CREATE TABLE CaseTable (
    CaseID INT PRIMARY KEY,
    CaseType VARCHAR(100),
    DateReported DATE,
    Description_Of_Case TEXT,
    ProgressPercentage DECIMAL(5,2) CHECK (ProgressPercentage BETWEEN 0 AND 100),
    Verdict VARCHAR(100),
    Stage VARCHAR(50),
    AssignedOfficer_ID INT,
    FOREIGN KEY (AssignedOfficer_ID) REFERENCES Police(PoliceID)
);

--------------------------------------------------------
-- 5. Criminal Table
--------------------------------------------------------
CREATE TABLE Criminal(  
    Criminal_ID INT PRIMARY KEY,  
    Name_ VARCHAR(100) NOT NULL,  
    Address VARCHAR(100) UNIQUE,  
    DateofBirth DATE,  
    Gender CHAR(1),  
    CriminalRecord TEXT,  
    CaseID INT,  
    Age INT NOT NULL,
    TrialDuration VARCHAR(50),
    FOREIGN KEY (CaseID) REFERENCES CaseTable(CaseID)
);

--------------------------------------------------------
-- 6. Evidence Table
--------------------------------------------------------
CREATE TABLE Evidence (
    EvidenceID INT PRIMARY KEY AUTO_INCREMENT,
    CaseID INT NOT NULL,
    CollectedBy INT,
    EvidenceType VARCHAR(100),
    Description TEXT,
    DateCollected DATE NOT NULL,
    StorageLocation VARCHAR(100),
    FOREIGN KEY (CaseID) REFERENCES CaseTable(CaseID),
    FOREIGN KEY (CollectedBy) REFERENCES Police(PoliceID)
);

--------------------------------------------------------
-- 7. CourtProceedings Table
--------------------------------------------------------
CREATE TABLE CourtProceedings (  
    ProceedingID INT PRIMARY KEY,  
    CaseID INT NOT NULL,  
    ProceedingDate DATE NOT NULL,  
    CourtName VARCHAR(100) NOT NULL,  
    JudgeName VARCHAR(100) NOT NULL,  
    ProceedingType VARCHAR(100),  
    PoliceID INT,  
    Remarks TEXT,  
    FOREIGN KEY (CaseID) REFERENCES CaseTable(CaseID),
    FOREIGN KEY (PoliceID) REFERENCES Police(PoliceID)
);

--------------------------------------------------------
-- INSERT DATA
--------------------------------------------------------

INSERT INTO Department VALUES
(1,'Cyber Crime','Ravi Verma','9876543210','ravi.verma@police.gov','2005-06-15'),
(2,'Homicide','Anita Desai','8765432109','anita.desai@police.gov','1998-03-22'),
(3,'Narcotics','Suresh Iyer','7654321098','suresh.iyer@police.gov','2001-11-05'),
(4,'Traffic Control','Meena Joshi','6543210987','meena.joshi@police.gov','2010-09-10'),
(5,'Forensics','Rajesh Khanna','5432109876','rajesh.khanna@police.gov','2003-01-18'),
(6,'Anti -Terrorism','Neha Kapoor','4321098765','neha.kapoor@police.gov','2007-07-30'),
(7,'Fraud Investigation','Amit Shah','3210987654','amit.shah@police.gov','2012-12-01');

INSERT INTO Police (PoliceID,PoliceName,Ranking,Email,PhoneNumber,Date_of_Birth,Age,Salary,Dept_ID) VALUES
(301,'Ravi Verma','Inspector','ravi.verma@police.gov','9876543210','1980-04-12',45,80000,1),
(302,'Anita Desai','Superintendent','anita.desai@police.gov','8765432109','1975-08-19',50,150000,2),
(303,'Suresh Iyer','Constable','suresh.iyer@police.gov','7654321098','1990-02-25',35,30000,3),
(304,'Meena Joshi','Inspector','meena.joshi@police.gov','6543210987','1985-06-30',40,80000,4),
(305,'Rajesh Khanna','Head Constable','rajesh.khanna@police.gov','5432109876','1988-11-11',37,45000,5),
(306,'Neha Kapoor','Deputy Commissioner','neha.kapoor@police.gov','4321098765','1973-03-03',52,175000,6),
(307,'Amit Shah','Inspector','amit.shah@police.gov','3210987654','1982-09-09',43,80000,7),
(308,'Vikram Malhotra','Inspector','vikram.malhotra@police.gov','9876501234','1984-01-15',41,82000,1),
(309,'Sunita Reddy','Constable','sunita.reddy@police.gov','8765409876','1991-07-21',34,32000,1),
(310,'Karan Gupta','Sub-Inspector','karan.gupta@police.gov','7654398765','1987-10-10',38,60000,2),
(311,'Pooja Sharma','Superintendent','pooja.sharma@police.gov','6543987654','1978-05-05',47,148000,2),
(312,'Alok Nair','Head Constable','alok.nair@police.gov','5439876543','1986-12-12',39,46000,3),
(313,'Rekha Patel','Inspector','rekha.patel@police.gov','4321987654','1981-02-28',44,81000,4),
(314,'Arvind Singh','Constable','arvind.singh@police.gov','3219876543','1993-09-19',32,31000,5),
(315,'Deepa Menon','Deputy Commissioner','deepa.menon@police.gov','2109876543','1970-06-25',55,180000,6);

INSERT INTO Station (StationName,Location,ContactNumber,Dept_ID,InChargeOfficer_ID) VALUES
('Central Station','Mumbai','9988776655',1,301),
('North Station','Delhi','8877665544',2,302),
('East Station','Kolkata','7766554433',3,303),
('West Station','Ahmedabad','6655443322',4,304),
('South Station','Chennai','5544332211',5,305),
('Metro Station','Bangalore','4433221100',6,306),
('Riverfront Station','Lucknow','3322110099',7,307);

INSERT INTO CaseTable VALUES
(401,'Cyber Fraud','2023-01-10','Unauthorized access to banking systems',80.50,'Pending','Investigation',301),
(402,'Murder','2022-11-05','Homicide in residential area',95.00,'Guilty','Trial',302),
(403,'Drug Possession','2023-03-15','Illegal narcotics found',60.00,'Pending','Investigation',303),
(404,'Traffic Violation','2023-04-20','Hit and run case',100.00,'Closed','Verdict Given',304),
(405,'Forgery','2022-12-01','Fake documents used',70.00,'Pending','Investigation',307),
(406,'Terror Threat','2023-05-25','Threat to transport',40.00,'Pending','Initial Review',306),
(407,'Bank Fraud','2023-06-10','Money laundering',85.00,'Pending','Investigation',305);

INSERT INTO Criminal VALUES
(501,'Rohan Mehta','12 MG Road','1990-07-15','M','Cyber fraud',401,34,'6 months'),
(502,'Priya Sharma','45 Park Street','1985-03-22','F','Murder',402,39,'2 years'),
(503,'Arjun Rao','78 Lake View','1992-11-30','M','Drug trafficking',403,32,'1 year'),
(504,'Sneha Kulkarni','23 Beach Road','1995-05-10','F','Hit and run',404,29,'6 months'),
(505,'Vikram Singh','90 Hilltop','1988-08-08','M','Forgery',405,36,'8 months'),
(506,'Zoya Khan','66 Garden Lane','1993-01-01','F','Terror links',406,31,'3 years'),
(507,'Manish Tiwari','34 Riverbank','1980-12-12','M','Bank fraud',407,44,'1 year');

INSERT INTO Evidence (EvidenceID,CaseID,CollectedBy,EvidenceType,Description,DateCollected,StorageLocation) VALUES
(601,401,301,'Digital Logs','Server logs','2023-01-11','Locker A-12'),
(602,402,302,'Knife','Blood weapon','2022-11-06','Vault B-03'),
(603,403,303,'Powder Sample','Narcotics sample','2023-03-16','Chem-02'),
(604,404,304,'CCTV Footage','Camera footage','2023-04-21','Locker A-07');

INSERT INTO CourtProceedings VALUES
(801,401,'2025-09-12','Mumbai High Court','Justice R. Mehta','Preliminary Hearing',301,'Evidence review'),
(802,402,'2025-09-13','Delhi Sessions Court','Justice A. Kapoor','Final Verdict',302,'Verdict announced'),
(803,403,'2025-09-14','Kolkata Criminal Court','Justice S. Banerjee','Witness Examination',303,'Testimony scheduled'),
(804,404,'2025-09-15','Chennai Tribunal','Justice M. Iyer','Verdict Review',304,'Review session');

--------------------------------------------------------
-- FIX FK Update
--------------------------------------------------------
ALTER TABLE CaseTable DROP FOREIGN KEY CaseTable_ibfk_1;

ALTER TABLE CaseTable
ADD FOREIGN KEY (AssignedOfficer_ID) REFERENCES Police(PoliceID)
ON DELETE SET NULL ON UPDATE CASCADE;

--------------------------------------------------------
-- DepartmentLog Table
--------------------------------------------------------
CREATE TABLE DepartmentLog (
  LogID INT AUTO_INCREMENT PRIMARY KEY,
  Dept_ID INT,
  ActionType VARCHAR(20),
  ActionTime TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

--------------------------------------------------------
-- TRIGGERS
--------------------------------------------------------

DELIMITER $$
CREATE TRIGGER log_case_insert
AFTER INSERT ON CaseTable
FOR EACH ROW
BEGIN
  INSERT INTO Evidence (CaseID, EvidenceType, Description, DateCollected, StorageLocation)
  VALUES (NEW.CaseID,'Auto-log','System generated',CURDATE(),'System');
END$$
DELIMITER ;

DELIMITER $$
CREATE TRIGGER update_case_on_criminal_insert
AFTER INSERT ON Criminal
FOR EACH ROW
BEGIN
  UPDATE CaseTable SET Stage='Trial Phase' WHERE CaseID=NEW.CaseID;
END$$
DELIMITER ;

DELIMITER $$
CREATE TRIGGER update_criminal_age
BEFORE INSERT ON Criminal
FOR EACH ROW
BEGIN
  SET NEW.Age = TIMESTAMPDIFF(YEAR, NEW.DateofBirth, CURDATE());
END$$
DELIMITER ;

DELIMITER $$
CREATE TRIGGER after_department_insert
AFTER INSERT ON Department
FOR EACH ROW
BEGIN
  INSERT INTO DepartmentLog (Dept_ID, ActionType) VALUES (NEW.Dept_ID, 'INSERT');
END$$
DELIMITER ;

DELIMITER $$
CREATE TRIGGER after_department_delete
AFTER DELETE ON Department
FOR EACH ROW
BEGIN
  INSERT INTO DepartmentLog (Dept_ID, ActionType) VALUES (OLD.Dept_ID, 'DELETE');
END$$
DELIMITER ;

DELIMITER $$
CREATE TRIGGER after_criminal_insert
AFTER INSERT ON Criminal
FOR EACH ROW
BEGIN
  IF (SELECT COUNT(*) FROM CourtProceedings WHERE CaseID = NEW.CaseID) = 0 THEN
    INSERT INTO CourtProceedings
    VALUES (NEW.Criminal_ID+1000,NEW.CaseID,CURDATE(),'District Court','To Be Assigned','Initial Hearing',NULL,
            CONCAT('Auto-generated proceeding for ',NEW.Name_));
  END IF;
END$$
DELIMITER ;

-- ------------------------------------------------------
-- VIEW
-- ------------------------------------------------------
CREATE OR REPLACE VIEW CriminalCaseSummaryView AS
SELECT 
    c.CaseID,
    c.CaseType,
    c.Description_Of_Case,
    c.DateReported,
    c.Stage,
    c.ProgressPercentage,
    c.Verdict,
    p.PoliceName AS AssignedOfficer,
    d.DepartmentType AS Department,
    cr.Name_ AS CriminalName,
    cr.Gender,
    cr.Age,
    cp.CourtName,
    cp.ProceedingType,
    cp.ProceedingDate,
    cp.Remarks
FROM CaseTable c
LEFT JOIN Police p ON c.AssignedOfficer_ID=p.PoliceID
LEFT JOIN Department d ON p.Dept_ID=d.Dept_ID
LEFT JOIN Criminal cr ON cr.CaseID=c.CaseID
LEFT JOIN CourtProceedings cp ON cp.CaseID=c.CaseID;

-------------------------------------------------------------

ALTER TABLE CaseTable DROP FOREIGN KEY fk_Police;
ALTER TABLE  CourtProceedings  DROP FOREIGN KEY fk_police_proceeding;
ALTER TABLE Police
MODIFY COLUMN PoliceID INT NOT NULL AUTO_INCREMENT;

ALTER TABLE CaseTable
ADD CONSTRAINT fk_Police
FOREIGN KEY (AssignedOfficer_ID) REFERENCES Police(PoliceID)
ON DELETE SET NULL
ON UPDATE CASCADE;

ALTER TABLE CourtProceedings
ADD CONSTRAINT fk_police_proceeding
FOREIGN KEY (PoliceID) REFERENCES Police(PoliceID)
ON DELETE SET NULL
ON UPDATE CASCADE;

SELECT * FROM Police;

DELIMITER //
CREATE TRIGGER log_case_insert
AFTER INSERT ON CaseTable
FOR EACH ROW
BEGIN
  INSERT INTO Evidence (EvidenceID, EvidenceType, CollectedBy, CollectedDate, CaseID)
  VALUES (
    (SELECT IFNULL(MAX(EvidenceID), 600) + 1 FROM Evidence),
    'Auto-log: Case Created',
    'System',
    CURDATE(),
    NEW.CaseID
  );
END //
DELIMITER ;

DELIMITER //
CREATE TRIGGER update_case_on_criminal_insert
AFTER INSERT ON Criminal
FOR EACH ROW
BEGIN
  UPDATE CaseTable
  SET Stage = 'Trial Phase'
  WHERE CaseID = NEW.CaseID;
END //
DELIMITER ;

DELIMITER //
CREATE TRIGGER update_criminal_age
BEFORE INSERT ON Criminal
FOR EACH ROW
BEGIN
  SET NEW.Age = TIMESTAMPDIFF(YEAR, NEW.DateofBirth, CURDATE());
END //
DELIMITER ;

CREATE TABLE DepartmentLog (
  LogID INT AUTO_INCREMENT PRIMARY KEY,
  Dept_ID INT,
  ActionType VARCHAR(20),
  ActionTime TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

DELIMITER $$

CREATE TRIGGER after_department_insert
AFTER INSERT ON Department
FOR EACH ROW
BEGIN
  INSERT INTO DepartmentLog (Dept_ID, ActionType)
  VALUES (NEW.Dept_ID, 'INSERT');
END$$

CREATE TRIGGER after_department_delete
AFTER DELETE ON Department
FOR EACH ROW
BEGIN
  INSERT INTO DepartmentLog (Dept_ID, ActionType)
  VALUES (OLD.Dept_ID, 'DELETE');
END$$

DELIMITER ;

DELIMITER $$

CREATE TRIGGER after_criminal_insert
AFTER INSERT ON Criminal
FOR EACH ROW
BEGIN
  IF (SELECT COUNT(*) FROM CourtProceedings WHERE CaseID = NEW.CaseID) = 0 THEN
    INSERT INTO CourtProceedings (
      ProceedingID, CaseID, ProceedingDate, CourtName, JudgeName, ProceedingType, PoliceID, Remarks
    )
    VALUES (
      NEW.Criminal_ID + 1000,
      NEW.CaseID,
      CURDATE(),
      'District Court',
      'To Be Assigned',
      'Initial Hearing',
      NULL,
      CONCAT('Auto-generated proceeding for criminal ', NEW.Name_)
    );
  END IF;
END$$

DELIMITER ;


DELIMITER $$

CREATE TRIGGER after_criminal_update
AFTER UPDATE ON Criminal
FOR EACH ROW
BEGIN
  -- Update remarks only if key fields changed
  IF NEW.CriminalRecord <> OLD.CriminalRecord 
     OR NEW.TrialDuration <> OLD.TrialDuration THEN

    UPDATE CourtProceedings
    SET Remarks = CONCAT(
        'Updated on ', DATE_FORMAT(NOW(), '%Y-%m-%d %H:%i'),
        ': Criminal record or trial info changed for ',
        NEW.Name_, 
        '. New record: ', COALESCE(NEW.CriminalRecord, 'N/A'),
        ', Trial duration: ', COALESCE(NEW.TrialDuration, 'N/A')
    )
    WHERE CaseID = NEW.CaseID;
  END IF;
END$$

DELIMITER ;

CREATE OR REPLACE VIEW CriminalCaseSummaryView AS
SELECT 
    c.CaseID,
    c.CaseType,
    c.Description_Of_Case,
    c.DateReported,
    c.Stage,
    c.ProgressPercentage,
    c.Verdict,

    -- Officer Info
    p.PoliceName AS AssignedOfficer,
    p.Ranking AS OfficerRank,
    p.PhoneNumber AS OfficerContact,

    -- Department Info
    d.DepartmentType AS Department,
    d.DepartmentHead AS DepartmentHead,

    -- Criminal Info
    cr.Name_ AS CriminalName,
    cr.Gender,
    cr.Age,
    cr.CriminalRecord,
    cr.TrialDuration,

    -- Court Info
    cp.CourtName,
    cp.JudgeName,
    cp.ProceedingType,
    cp.ProceedingDate,
    cp.Remarks AS CourtRemarks

FROM CaseTable c
LEFT JOIN Police p ON c.AssignedOfficer_ID = p.PoliceID
LEFT JOIN Department d ON p.Dept_ID = d.Dept_ID
LEFT JOIN Criminal cr ON c.CaseID = cr.CaseID
LEFT JOIN CourtProceedings cp ON c.CaseID = cp.CaseID;

SELECT 
    CaseID,
    CaseType,
    AssignedOfficer,
    CriminalName,
    Verdict,
    ProgressPercentage,
    CourtName,
    ProceedingType
FROM CriminalCaseSummaryView
WHERE Verdict <> 'Closed'
ORDER BY ProgressPercentage DESC;

SELECT Department, COUNT(*) AS ActiveCases
FROM CriminalCaseSummaryView
WHERE Verdict <> 'Closed'
GROUP BY Department;

SELECT AssignedOfficer, ROUND(AVG(ProgressPercentage), 2) AS AvgProgress
FROM CriminalCaseSummaryView
GROUP BY AssignedOfficer;

SELECT Gender, COUNT(*) AS CriminalCount
FROM CriminalCaseSummaryView
GROUP BY Gender;



DELIMITER //
CREATE TRIGGER trg_update_case_progress
AFTER INSERT ON Evidence
FOR EACH ROW
BEGIN
    UPDATE CaseTable
    SET ProgressPercentage = LEAST(ProgressPercentage + 5, 100)
    WHERE CaseID = NEW.CaseID;
END //
DELIMITER ;

ALTER TABLE Evidence
ADD COLUMN ImageFile VARCHAR(255);

ALTER TABLE Criminal
MODIFY COLUMN Criminal_ID INT NOT NULL AUTO_INCREMENT;
SELECT * FROM Criminal;