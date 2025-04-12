using System.Text.Json.Serialization;

namespace Boardify.Models
{
    public class Board
    {
        [JsonPropertyName("id")]
        required public string Id { get; set; }
        [JsonPropertyName("name")]
        required public string Name { get; set; }
        [JsonPropertyName("tickets")]
        required public List<Ticket> Tickets { get; set; }
        [JsonPropertyName("stages")]
        required public List<Stage> Stages { get; set; }
        [JsonPropertyName("tags")]
        required public List<Tag> Tags { get; set; }
    }

    public class BoardCreate
    {
        [JsonPropertyName("name")]
        required public string Name { get; set; }
        [JsonPropertyName("stages")]
        required public List<Stage> Stages { get; set; }
        [JsonPropertyName("tags")]
        required public List<Tag> Tags { get; set; }
    }

    public class  BoardUpdate
    {
        [JsonPropertyName("name")]
        required public string Name { get; set; }
    }

    public class BoardOverview
    {
        [JsonPropertyName("id")]
        required public string Id { get; set; }
        [JsonPropertyName("name")]
        required public string Name { get; set; }
        [JsonPropertyName("tickets_count")]
        required public int TicketsCount { get; set; }
        [JsonPropertyName("done_tickets_count")]
        required public int DoneTicketsCount { get; set; }
    }

    public class Stage
    {
        [JsonPropertyName("nr")]
        required public int Nr { get; set; }
        [JsonPropertyName("name")]
        required public string Name { get; set; }
    }

    public class Tag
    {
        [JsonPropertyName("id")]
        required public int Id { get; set; }
        [JsonPropertyName("name")]
        required public string Name { get; set; }
    }
}
