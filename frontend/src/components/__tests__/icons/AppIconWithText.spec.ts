import { mount } from "@vue/test-utils";
import { describe, expect, it } from "vitest";
import AppIconWithText from "../../icons/AppIconWithText.vue";

describe("AppIconWithText", () => {
	it("renders properly", () => {
		const wrapper = mount(AppIconWithText);
		expect(wrapper.exists()).toBe(true);
		expect(wrapper.text()).toBe("Meow // Sync");
	});
});
