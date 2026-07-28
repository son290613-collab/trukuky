<?php
declare(strict_types=1);

function format_vnd($amount): string
{
    return number_format((float) $amount, 0, ',', '.') . '₫';
}

function format_date(string $date): string
{
    $ts = strtotime($date);
    return $ts ? date('d/m/Y', $ts) : $date;
}

function e(?string $value): string
{
    return htmlspecialchars($value ?? '', ENT_QUOTES, 'UTF-8');
}

function json_input(): array
{
    $raw = file_get_contents('php://input');
    $data = json_decode($raw, true);
    return is_array($data) ? $data : [];
}

function json_out($data, int $status = 200): never
{
    http_response_code($status);
    header('Content-Type: application/json; charset=utf-8');
    echo json_encode($data, JSON_UNESCAPED_UNICODE);
    exit;
}
