using Boardify.Models;
using Microsoft.Net.Http.Headers;
using System.Text;
using System.Text.Json;

namespace Boardify.Services
{
    public class BackendService
    {
        private readonly HttpClient _httpClient;

        public BackendService(HttpClient httpClient, IConfiguration config)
        {
            _httpClient = httpClient;

            _httpClient.BaseAddress = new Uri(config["BackendUri"]!);
        }

        private async Task<T> FetchAsync<T>(string url, HttpMethod? method = null, Object? body = null)
        {
            var request = new HttpRequestMessage(method ?? HttpMethod.Get, url);
            if (body != null)
            {
                request.Content = new StringContent(JsonSerializer.Serialize(body), Encoding.UTF8, "application/json");
            }
            var response = await _httpClient.SendAsync(request);
            response.EnsureSuccessStatusCode();
            var content = await response.Content.ReadAsStringAsync();
            return JsonSerializer.Deserialize<T>(content)!;
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
}
