using System.Text.Json.Serialization;

namespace Boardify.Models;

public class Board
{
    [JsonPropertyName("id")] public required string Id { get; set; }

    [JsonPropertyName("name")] public required string Name { get; set; }

    [JsonPropertyName("tickets")] public required List<Ticket> Tickets { get; set; }

    [JsonPropertyName("stages")] public required List<Stage> Stages { get; set; }
}

public class BoardCreate
{
    [JsonPropertyName("name")] public required string Name { get; set; }

    [JsonPropertyName("stages")] public required List<Stage> Stages { get; set; }

    [JsonPropertyName("tags")] public required List<Tag> Tags { get; set; }
}

public class BoardUpdate
{
    [JsonPropertyName("name")] public required string Name { get; set; }
}

public class BoardOverview
{
    [JsonPropertyName("id")] public required string Id { get; set; }

    [JsonPropertyName("name")] public required string Name { get; set; }

    [JsonPropertyName("tickets_count")] public required int TicketsCount { get; set; }

    [JsonPropertyName("done_tickets_count")]
    public required int DoneTicketsCount { get; set; }
}

public class Stage
{
    [JsonPropertyName("nr")] public required int Nr { get; set; }

    [JsonPropertyName("name")] public required string Name { get; set; }
}

public class Tag
{
    [JsonPropertyName("nr")] public required int Nr { get; set; }

    [JsonPropertyName("name")] public required string Name { get; set; }
}