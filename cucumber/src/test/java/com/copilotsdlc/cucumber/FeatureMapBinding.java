package com.copilotsdlc.cucumber;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;

final class FeatureMapBinding {
    private static final ObjectMapper JSON = new ObjectMapper();
    private final Path repository;
    private final JsonNode metadata;
    private FeatureMapBinding(Path repository, JsonNode metadata) {
        this.repository = repository;
        this.metadata = metadata;
    }
    static FeatureMapBinding open(String featureId) throws IOException {
        if (!featureId.matches("[a-z][a-z0-9-]*")) throw new IllegalArgumentException("Unsafe feature id");
        Path root = Path.of(System.getProperty("sdlc.repository.root", "..")).toAbsolutePath().normalize();
        Path source = root.resolve("docs/feature-map/" + featureId + ".md").normalize();
        String content = Files.readString(source);
        for (String header : new String[]{"## Sub-features","## How to get to it","## Driving it","## Gotchas","## SDLC Cucumber Binding"}) {
            if (!content.contains(header)) throw new IllegalStateException("Feature Map missing: " + header);
        }
        String fence = new String(new char[]{96,96,96});
        int start = content.indexOf(fence + "json", content.indexOf("## SDLC Cucumber Binding"));
        if (start < 0) throw new IllegalStateException("Feature Map binding JSON is missing");
        int end = content.indexOf(fence, start + fence.length() + 4);
        if (end < 0) throw new IllegalStateException("Feature Map binding JSON is unterminated");
        JsonNode meta = JSON.readTree(content.substring(start + fence.length() + 4, end));
        if (!featureId.equals(meta.path("feature_id").asText())) throw new IllegalStateException("Feature id mismatch");
        for (String name : new String[]{"gherkin","scenario","contract","fixture"}) {
            String link = meta.path(name).asText();
            Path linked = root.resolve(link).normalize();
            if (link.isEmpty() || !linked.startsWith(root) || !Files.isRegularFile(linked)) {
                throw new IllegalStateException("Feature Map target unavailable or unsafe: " + name);
            }
        }
        if (!Files.readString(root.resolve(meta.path("gherkin").asText()))
                .contains("@feature_" + featureId.replace("-", "_"))) {
            throw new IllegalStateException("Gherkin tag does not match Feature Map id");
        }
        return new FeatureMapBinding(root, meta);
    }
    String fixtureStatus() throws IOException {
        Path file = repository.resolve(metadata.path("fixture").asText());
        return JSON.readTree(Files.readString(file)).path("status").asText();
    }
    String scenarioId() { return metadata.path("scenario_id").asText(); }
}
