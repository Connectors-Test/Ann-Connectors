USE master;
GO

-- Create new DB if needed
IF NOT EXISTS (SELECT name FROM sys.databases WHERE name = N'SCAI')
BEGIN
    CREATE DATABASE SCAI;
END
GO

USE SCAI;
GO

-- Drop Users table if it exists
IF OBJECT_ID('Users', 'U') IS NOT NULL
    DROP TABLE Users;
GO

-- Create Users table
CREATE TABLE Users (
    id INT PRIMARY KEY IDENTITY(1,1),
    name NVARCHAR(100) NOT NULL,
    email NVARCHAR(255) UNIQUE NOT NULL,
    role NVARCHAR(50),
    experience_years INT CHECK (experience_years >= 0),
    skills NVARCHAR(MAX),
    created_at DATETIME DEFAULT GETDATE()
);
GO

-- Insert seed data
INSERT INTO Users (name, email, role, experience_years, skills) VALUES
('Alice', 'alice@example.com', 'Data Scientist', 4, 'Python, SQL, Machine Learning'),
('Bob', 'bob@example.com', 'Backend Developer', 2, 'Node.js, MongoDB, MSSQL'),
('Charlie', 'charlie@example.com', 'DevOps Engineer', 5, 'Docker, Kubernetes, Azure'),
('Grace', 'grace@example.com', 'Full Stack Developer', 3, 'React, Node.js, Firebase'),
('Neo', 'neo@matrix.io', 'AI Researcher', 10, 'C++, PyTorch, Reality Bending');
GO