using System.Net.Http.Headers;
using System.Text;
using System.Text.Json;
using Blazored.LocalStorage;
using Boardify.Models;

namespace Boardify.Services;

public class BackendService
{
    private const string TokenStorageKey = "auth_token";
    private readonly HttpClient _httpClient;
    private readonly ILocalStorageService _localStorage;

    public BackendService(HttpClient httpClient, IConfiguration config, ILocalStorageService localStorage)
    {
        _httpClient = httpClient;
        _localStorage = localStorage;

        _httpClient.BaseAddress = new Uri(config["BackendUri"]!);
    }

    private async Task<T> FetchAsync<T>(string url, HttpMethod? method = null, object? body = null)
    {
        var request = new HttpRequestMessage(method ?? HttpMethod.Get, url);
        var token = await GetToken();
        if (token != null)
            request.Headers.Authorization = new AuthenticationHeaderValue(token.TokenType, token.AccessToken);
        if (body != null)
            request.Content = new StringContent(JsonSerializer.Serialize(body), Encoding.UTF8, "application/json");
        var response = await _httpClient.SendAsync(request);
        response.EnsureSuccessStatusCode();
        var content = await response.Content.ReadAsStringAsync();
        return JsonSerializer.Deserialize<T>(content)!;
    }

    private async Task SetToken(Token token)
    {
        await _localStorage.SetItemAsync(TokenStorageKey, JsonSerializer.Serialize(token));
    }

    public async Task<bool> IsLoggedIn()
    {
        var token = await GetToken();
        return token != null;
    }

    private async Task<Token?> GetToken()
    {
        var token = await _localStorage.GetItemAsync<string>(TokenStorageKey);
        return string.IsNullOrEmpty(token) ? null : JsonSerializer.Deserialize<Token>(token);
    }

    public async Task<User> Register(UserCredentials userCredentials)
    {
        return await FetchAsync<User>("/users/register", HttpMethod.Post, userCredentials);
    }

    public async Task Login(UserCredentials userCredentials)
    {
        var token = await FetchAsync<Token>("/users/login", HttpMethod.Post, userCredentials);
        await SetToken(token);
    }

    public async Task Logout()
    {
        await _localStorage.RemoveItemAsync(TokenStorageKey);
    }

    public async Task<User> GetUser()
    {
        return await FetchAsync<User>("/users/me");
    }

    public async Task<List<BoardOverview>> GetBoardsOverview()
    {
        return await FetchAsync<List<BoardOverview>>("/boards");
    }

    public async Task<Board> GetBoard(string id)
    {
        return await FetchAsync<Board>($"/boards/{id}");
    }

    public async Task<Board> CreateBoard(BoardCreate board)
    {
        return await FetchAsync<Board>("/boards", HttpMethod.Post, board);
    }

    public async Task<Board> UpdateBoard(string id, BoardUpdate board)
    {
        return await FetchAsync<Board>($"/boards/{id}", HttpMethod.Patch, board);
    }

    public async Task DeleteBoard(string id)
    {
        await FetchAsync<object>($"/boards/{id}", HttpMethod.Delete);
    }

    public async Task<Ticket> CreateTicket(string boardId, TicketCreate ticket)
    {
        return await FetchAsync<Ticket>($"/tickets?board_id={boardId}", HttpMethod.Post, ticket);
    }

    public async Task<Ticket> UpdateTicket(string ticketId, TicketUpdate ticketUpdate)
    {
        return await FetchAsync<Ticket>($"/tickets/{ticketId}", HttpMethod.Patch, ticketUpdate);
    }

    public async Task DeleteTicket(string ticketId)
    {
        await FetchAsync<object>($"/tickets/{ticketId}", HttpMethod.Delete);
    }
}