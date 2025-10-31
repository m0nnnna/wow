<?php
$host = '';  // DB host
$dbname = '';  // Your characters database name
$user = '';  // DB username
$pass = '';  // DB password

try {
    $pdo_chars = new PDO("mysql:host=$host;dbname=$dbname;charset=utf8mb4", $user, $pass);
    $pdo_chars->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
} catch (PDOException $e) {
    die("Database connection failed: " . $e->getMessage());
}
?>