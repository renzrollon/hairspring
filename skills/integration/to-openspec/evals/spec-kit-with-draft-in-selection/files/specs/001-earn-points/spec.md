# Feature Specification: Earn points at the POS

**Feature Branch**: `001-earn-points`

**Created**: 2026-10-20

**Status**: Draft

**Input**: User description: "Members earn points when they pay at the till"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Earn points on purchase (Priority: P1)

A member scans the app QR code at the till and earns points for the purchase.

**Acceptance Scenarios**:

1. **Given** a member pays SGD 12.80, **When** the POS sends the purchase event, **Then** a pending transaction of 12 points is created

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST create a pending points transaction for each completed purchase event.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Members see pending points in the app after checkout.
