using System.Text.Json.Serialization;

namespace Boardify.Models
{
    public class Ticket
    {
        [JsonPropertyName("id")]
        required public string Id { get; set; }
        [JsonPropertyName("stage_nr")]
        public int StageNr { get; set; }
        [JsonPropertyName("title")]
        required public string Title { get; set; }
        [JsonPropertyName("description")]
        required public string Description { get; set; }
        [JsonPropertyName("created_at")]
        public DateTime CreatedAt { get; set; }
        [JsonPropertyName("due_at")]
        public DateTime? DueAt { get; set; }
        [JsonPropertyName("is_done")]
        public bool IsDone { get; set; }

        public string CreatedDateFormatted => CreatedAt.ToString("dd.MM.yyyy");
        public string? DueDateFormatted => DueAt?.ToString("dd.MM.yyyy");
    }

    public class TicketCreate
    {
        [JsonPropertyName("stage_nr")]
        public int StageNr { get; set; }
        [JsonPropertyName("title")]
        required public string Title { get; set; }
        [JsonPropertyName("description")]
        required public string Description { get; set; }
        [JsonPropertyName("due_at")]
        public DateTime? DueAt { get; set; }
    }

    public class TicketUpdate
    {
        [JsonPropertyName("stage_nr")]
        public int? StageNr { get; set; }
        [JsonPropertyName("title")]
        public string? Title { get; set; }
        [JsonPropertyName("description")]
        public string? Description { get; set; }
        [JsonPropertyName("due_at")]
        public DateTime? DueAt { get; set; }
    }
}
