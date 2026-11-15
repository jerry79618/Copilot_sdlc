@feature_manual_review @demo @regression
Feature: Cross-system manual review verification
  In an isolated sandbox, verify an approved review journey

  Background:
    Given the Feature Map "manual-review" describes this behavior

  @smoke
  Scenario: A manual review case reaches expected downstream states
    Given the approved synthetic review fixture is ready
    When the risk system provisions the review case
    And the application system submits the review request
    And the sync system processes the review event
    Then the risk status should be "MANUAL_REVIEW"
    And the application status should be "PENDING_REVIEW"
    And the sync event should be delivered

  Scenario: An application cannot be submitted before risk preparation
    When the application system submits the review request without preparation
    Then the operation must be blocked because "risk prerequisite is not ready"

  Scenario: Synchronization cannot run before an application exists
    When the sync system processes a review event without an application
    Then the operation must be blocked because "application prerequisite is not ready"
