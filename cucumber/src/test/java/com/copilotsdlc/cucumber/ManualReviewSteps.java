package com.copilotsdlc.cucumber;
import io.cucumber.java.en.Given;
import io.cucumber.java.en.When;
import io.cucumber.java.en.Then;
import org.junit.Assert;

public final class ManualReviewSteps {
    private final DemoReviewSystems systems = new DemoReviewSystems();
    private FeatureMapBinding map;
    private String fixtureStatus;
    private String blockedReason;

    @Given("the Feature Map {string} describes this behavior")
    public void loadMap(String name) throws Exception {
        map = FeatureMapBinding.open(name);
        Assert.assertEquals("REVIEW-001", map.scenarioId());
    }
    @Given("the approved synthetic review fixture is ready")
    public void prepareFixture() throws Exception {
        Assert.assertNotNull(map);
        fixtureStatus = map.fixtureStatus();
        Assert.assertEquals("MANUAL_REVIEW", fixtureStatus);
    }
    @When("the risk system provisions the review case")
    public void provision() { systems.provision(fixtureStatus); }
    @When("the application system submits the review request")
    public void submit() { systems.submit(); }
    @When("the sync system processes the review event")
    public void sync() { systems.sync(); }
    @Then("the risk status should be {string}")
    public void risk(String expected) { Assert.assertEquals(expected, systems.risk()); }
    @Then("the application status should be {string}")
    public void application(String expected) { Assert.assertEquals(expected, systems.application()); }
    @Then("the sync event should be delivered")
    public void delivered() { Assert.assertTrue(systems.delivered()); }
    @When("the application system submits the review request without preparation")
    public void submitWithoutRisk() {
        try { systems.submit(); Assert.fail("Missing prerequisite should block submission"); }
        catch (IllegalStateException blocked) { blockedReason = blocked.getMessage(); }
    }
    @When("the sync system processes a review event without an application")
    public void syncWithoutApplication() {
        try { systems.sync(); Assert.fail("Missing prerequisite should block synchronization"); }
        catch (IllegalStateException blocked) { blockedReason = blocked.getMessage(); }
    }
    @Then("the operation must be blocked because {string}")
    public void assertBlock(String expected) { Assert.assertEquals(expected, blockedReason); }
}
