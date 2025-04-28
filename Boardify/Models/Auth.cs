using System.Text.Json.Serialization;

namespace Boardify.Models;

public class User
{
    [JsonPropertyName("username")] public required string Username { get; set; }

    [JsonPropertyName("id")] public required string Id { get; set; }
}

public class UserCredentials
{
    [JsonPropertyName("username")] public required string Username { get; set; }

    [JsonPropertyName("password")] public required string Password { get; set; }
}

public class Token
{
    [JsonPropertyName("access_token")] public required string AccessToken { get; set; }

    [JsonPropertyName("token_type")] public required string TokenType { get; set; }
}