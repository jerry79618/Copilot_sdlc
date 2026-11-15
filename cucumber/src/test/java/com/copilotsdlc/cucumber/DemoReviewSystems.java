package com.copilotsdlc.cucumber;
/** Synthetic adapter only. No network or production database writes. */
final class DemoReviewSystems {
    private String risk = "NOT_FOUND";
    private String application = "NOT_SUBMITTED";
    private boolean delivered = false;
    void provision(String state) {
        if (!"MANUAL_REVIEW".equals(state)) throw new IllegalArgumentException("Invalid synthetic state");
        risk = state;
    }
    void submit() {
        if (!"MANUAL_REVIEW".equals(risk)) throw new IllegalStateException("risk prerequisite is not ready");
        application = "PENDING_REVIEW";
    }
    void sync() {
        if (!"PENDING_REVIEW".equals(application)) throw new IllegalStateException("application prerequisite is not ready");
        delivered = true;
    }
    String risk() { return risk; }
    String application() { return application; }
    boolean delivered() { return delivered; }
}
