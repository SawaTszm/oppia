# Copyright 2019 The Oppia Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS-IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""File for compiling and checking typescript."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys

# TODO(#15567): This can be removed after Literal in utils.py is loaded
# from typing instead of typing_extensions, this will be possible after
# we migrate to Python 3.8.
from scripts import common  # isort:skip pylint: disable=wrong-import-position, unused-import

from core import utils # isort:skip

import yaml # isort:skip

from typing import List, Optional, Sequence  # isort:skip

# Contains the name of all files that are not strictly typed.
# This list must be kept up-to-date; the changes (only remove) should be done
# manually.
# Please keep the list in alphabetical order.
# NOTE TO DEVELOPERS: do not add any new files to this list without asking
# @vojtechjelinek first.
# pylint: disable=line-too-long, single-line-pragma
TS_STRICT_EXCLUDE_PATHS = [
    'core/templates/App.ts',
    'core/templates/AppSpec.ts',
    'core/templates/Polyfills.ts',
    'core/templates/app.constants.ajs.ts',
    'core/templates/components/angular-html-bind/angular-html-bind-wrapper.directive.spec.ts',
    'core/templates/components/angular-html-bind/angular-html-bind-wrapper.directive.ts',
    'core/templates/components/button-directives/hint-and-solution-buttons.component.spec.ts',
    'core/templates/components/button-directives/hint-and-solution-buttons.component.ts',
    'core/templates/components/ck-editor-helpers/ck-editor-4-rte.component.ts',
    'core/templates/components/ck-editor-helpers/ck-editor-4-widgets.initializer.ts',
    'core/templates/components/ck-editor-helpers/ck-editor-copy-toolbar/ck-editor-copy-toolbar.component.spec.ts',
    'core/templates/components/ck-editor-helpers/ck-editor-copy-toolbar/ck-editor-copy-toolbar.component.ts',
    'core/templates/components/common-layout-directives/common-elements/answer-content-modal.controller.spec.ts',
    'core/templates/components/common-layout-directives/common-elements/confirm-or-cancel-modal.controller.spec.ts',
    'core/templates/components/common-layout-directives/common-elements/confirm-or-cancel-modal.controller.ts',
    'core/templates/components/concept-card/concept-card.component.spec.ts',
    'core/templates/components/concept-card/concept-card.component.ts',
    'core/templates/components/entity-creation-services/story-creation.service.spec.ts',
    'core/templates/components/entity-creation-services/story-creation.service.ts',
    'core/templates/components/entity-creation-services/topic-creation.service.spec.ts',
    'core/templates/components/entity-creation-services/topic-creation.service.ts',
    'core/templates/components/forms/custom-forms-directives/apply-validation.directive.spec.ts',
    'core/templates/components/forms/custom-forms-directives/apply-validation.directive.ts',
    'core/templates/components/forms/custom-forms-directives/html-select.component.spec.ts',
    'core/templates/components/forms/custom-forms-directives/html-select.component.ts',
    'core/templates/components/forms/custom-forms-directives/object-editor.directive.ts',
    'core/templates/components/forms/custom-forms-directives/require-is-float.directive.spec.ts',
    'core/templates/components/forms/custom-forms-directives/require-is-float.directive.ts',
    'core/templates/components/forms/custom-forms-directives/select2-dropdown.directive.ts',
    'core/templates/components/forms/custom-forms-directives/thumbnail-uploader.component.spec.ts',
    'core/templates/components/forms/custom-forms-directives/thumbnail-uploader.component.ts',
    'core/templates/components/forms/schema-based-editors/schema-based-bool-editor.component.spec.ts',
    'core/templates/components/forms/schema-based-editors/schema-based-bool-editor.component.ts',
    'core/templates/components/forms/schema-based-editors/schema-based-choices-editor.component.spec.ts',
    'core/templates/components/forms/schema-based-editors/schema-based-choices-editor.component.ts',
    'core/templates/components/forms/schema-based-editors/schema-based-custom-editor.component.spec.ts',
    'core/templates/components/forms/schema-based-editors/schema-based-custom-editor.component.ts',
    'core/templates/components/forms/schema-based-editors/schema-based-dict-editor.component.spec.ts',
    'core/templates/components/forms/schema-based-editors/schema-based-dict-editor.component.ts',
    'core/templates/components/forms/schema-based-editors/schema-based-editor.component.spec.ts',
    'core/templates/components/forms/schema-based-editors/schema-based-editor.component.ts',
    'core/templates/components/forms/schema-based-editors/schema-based-expression-editor.component.spec.ts',
    'core/templates/components/forms/schema-based-editors/schema-based-expression-editor.component.ts',
    'core/templates/components/forms/schema-based-editors/schema-based-float-editor.component.spec.ts',
    'core/templates/components/forms/schema-based-editors/schema-based-float-editor.component.ts',
    'core/templates/components/forms/schema-based-editors/schema-based-html-editor.component.spec.ts',
    'core/templates/components/forms/schema-based-editors/schema-based-html-editor.component.ts',
    'core/templates/components/forms/schema-based-editors/schema-based-int-editor.component.spec.ts',
    'core/templates/components/forms/schema-based-editors/schema-based-int-editor.component.ts',
    'core/templates/components/forms/schema-based-editors/schema-based-list-editor.component.spec.ts',
    'core/templates/components/forms/schema-based-editors/schema-based-list-editor.component.ts',
    'core/templates/components/forms/schema-based-editors/schema-based-unicode-editor.component.spec.ts',
    'core/templates/components/forms/schema-based-editors/schema-based-unicode-editor.component.ts',
    'core/templates/components/forms/schema-viewers/schema-based-custom-viewer.directive.spec.ts',
    'core/templates/components/forms/schema-viewers/schema-based-dict-viewer.directive.spec.ts',
    'core/templates/components/forms/schema-viewers/schema-based-dict-viewer.directive.ts',
    'core/templates/components/forms/schema-viewers/schema-based-html-viewer.directive.spec.ts',
    'core/templates/components/forms/schema-viewers/schema-based-list-viewer.directive.spec.ts',
    'core/templates/components/forms/schema-viewers/schema-based-primitive-viewer.directive.spec.ts',
    'core/templates/components/forms/schema-viewers/schema-based-primitive-viewer.directive.ts',
    'core/templates/components/forms/schema-viewers/schema-based-unicode-viewer.directive.spec.ts',
    'core/templates/components/forms/schema-viewers/schema-based-viewer.directive.spec.ts',
    'core/templates/components/forms/validators/has-length-at-least.filter.ts',
    'core/templates/components/forms/validators/has-length-at-most.filter.ts',
    'core/templates/components/forms/validators/is-at-least.filter.spec.ts',
    'core/templates/components/forms/validators/is-at-least.filter.ts',
    'core/templates/components/forms/validators/is-at-most.filter.spec.ts',
    'core/templates/components/forms/validators/is-at-most.filter.ts',
    'core/templates/components/forms/validators/is-float.filter.spec.ts',
    'core/templates/components/forms/validators/is-float.filter.ts',
    'core/templates/components/forms/validators/is-integer.filter.spec.ts',
    'core/templates/components/forms/validators/is-integer.filter.ts',
    'core/templates/components/forms/validators/is-nonempty.filter.spec.ts',
    'core/templates/components/forms/validators/is-nonempty.filter.ts',
    'core/templates/components/forms/validators/schema-validators.spec.ts',
    'core/templates/components/oppia-angular-root.component.spec.ts',
    'core/templates/components/oppia-angular-root.component.ts',
    'core/templates/components/question-directives/modal-templates/question-editor-modal.controller.spec.ts',
    'core/templates/components/question-directives/modal-templates/question-editor-modal.controller.ts',
    'core/templates/components/question-directives/modal-templates/question-editor-save-modal.component.ts',
    'core/templates/components/question-directives/question-editor/question-editor.component.spec.ts',
    'core/templates/components/question-directives/question-editor/question-editor.component.ts',
    'core/templates/components/question-directives/question-misconception-editor/question-misconception-editor.component.spec.ts',
    'core/templates/components/question-directives/question-misconception-editor/question-misconception-editor.component.ts',
    'core/templates/components/question-directives/question-misconception-editor/tag-misconception-modal-component.spec.ts',
    'core/templates/components/question-directives/question-misconception-editor/tag-misconception-modal-component.ts',
    'core/templates/components/question-directives/question-misconception-selector/question-misconception-selector.component.spec.ts',
    'core/templates/components/question-directives/question-misconception-selector/question-misconception-selector.component.ts',
    'core/templates/components/question-directives/question-player/question-player-concept-card-modal.controller.spec.ts',
    'core/templates/components/question-directives/question-player/question-player.component.spec.ts',
    'core/templates/components/question-directives/question-player/question-player.component.ts',
    'core/templates/components/question-directives/question-player/skill-mastery-modal.controller.spec.ts',
    'core/templates/components/question-directives/questions-list/questions-list.component.spec.ts',
    'core/templates/components/question-directives/questions-list/questions-list.component.ts',
    'core/templates/components/ratings/rating-display/rating-display.component.ts',
    'core/templates/components/review-material-editor/review-material-editor.component.ts',
    'core/templates/components/rubrics-editor/rubrics-editor.component.spec.ts',
    'core/templates/components/rubrics-editor/rubrics-editor.component.ts',
    'core/templates/components/save-pending-changes/save-pending-changes-modal.component.ts',
    'core/templates/components/score-ring/score-ring.component.ts',
    'core/templates/components/shared-component.module.ts',
    'core/templates/components/skill-selector/questions-list-select-skill-modal.controller.spec.ts',
    'core/templates/components/skill-selector/select-skill-modal.component.spec.ts',
    'core/templates/components/skills-mastery-list/skills-mastery-list-concept-card-modal.controller.spec.ts',
    'core/templates/components/stale-tab-info/stale-tab-info-modal.component.ts',
    'core/templates/components/state-directives/answer-group-editor/answer-group-editor.component.spec.ts',
    'core/templates/components/state-directives/answer-group-editor/answer-group-editor.component.ts',
    'core/templates/components/state-directives/hint-editor/hint-editor.component.spec.ts',
    'core/templates/components/state-directives/hint-editor/hint-editor.component.ts',
    'core/templates/components/state-directives/outcome-editor/outcome-destination-editor.component.spec.ts',
    'core/templates/components/state-directives/outcome-editor/outcome-destination-editor.component.ts',
    'core/templates/components/state-directives/outcome-editor/outcome-editor.component.spec.ts',
    'core/templates/components/state-directives/outcome-editor/outcome-editor.component.ts',
    'core/templates/components/state-directives/response-header/response-header.component.spec.ts',
    'core/templates/components/state-directives/response-header/response-header.component.ts',
    'core/templates/components/state-directives/rule-editor/rule-editor.component.spec.ts',
    'core/templates/components/state-directives/rule-editor/rule-editor.component.ts',
    'core/templates/components/state-directives/rule-editor/rule-type-selector.directive.ts',
    'core/templates/components/state-directives/solution-editor/solution-editor.component.spec.ts',
    'core/templates/components/state-directives/solution-editor/solution-editor.component.ts',
    'core/templates/components/state-directives/solution-editor/solution-explanation-editor.component.ts',
    'core/templates/components/state-editor/state-content-editor/state-content-editor.component.spec.ts',
    'core/templates/components/state-editor/state-content-editor/state-content-editor.component.ts',
    'core/templates/components/state-editor/state-editor.component.spec.ts',
    'core/templates/components/state-editor/state-editor.component.ts',
    'core/templates/components/state-editor/state-hints-editor/state-hints-editor.component.spec.ts',
    'core/templates/components/state-editor/state-hints-editor/state-hints-editor.component.ts',
    'core/templates/components/state-editor/state-interaction-editor/state-interaction-editor.component.spec.ts',
    'core/templates/components/state-editor/state-interaction-editor/state-interaction-editor.component.ts',
    'core/templates/components/state-editor/state-responses-editor/state-responses.component.spec.ts',
    'core/templates/components/state-editor/state-responses-editor/state-responses.component.ts',
    'core/templates/components/state-editor/state-solution-editor/state-solution-editor.component.spec.ts',
    'core/templates/components/state-editor/state-solution-editor/state-solution-editor.component.ts',
    'core/templates/components/statistics-directives/completion-graph.component.ts',
    'core/templates/components/summary-tile/learner-story-summary-tile.component.spec.ts',
    'core/templates/components/summary-tile/learner-story-summary-tile.component.ts',
    'core/templates/components/summary-tile/learner-topic-goals-summary-tile.component.spec.ts',
    'core/templates/components/summary-tile/learner-topic-goals-summary-tile.component.ts',
    'core/templates/components/summary-tile/learner-topic-summary-tile.component.spec.ts',
    'core/templates/components/summary-tile/learner-topic-summary-tile.component.ts',
    'core/templates/components/summary-tile/story-summary-tile.component.spec.ts',
    'core/templates/components/summary-tile/subtopic-summary-tile.component.spec.ts',
    'core/templates/components/summary-tile/subtopic-summary-tile.component.ts',
    'core/templates/components/summary-tile/topic-summary-tile.component.ts',
    'core/templates/components/unsaved-changes-status-info/unsaved-changes-status-info-modal.component.ts',
    'core/templates/components/version-diff-visualization/version-diff-visualization.component.spec.ts',
    'core/templates/components/version-diff-visualization/version-diff-visualization.component.ts',
    'core/templates/directives/angular-html-bind.directive.ts',
    'core/templates/directives/focus-on.directive.spec.ts',
    'core/templates/directives/mathjax-bind.directive.ts',
    'core/templates/domain/collection/collection-update.service.spec.ts',
    'core/templates/domain/collection/collection-update.service.ts',
    'core/templates/domain/collection/editable-collection-backend-api.service.spec.ts',
    'core/templates/domain/editor/undo_redo/undo-redo.service.spec.ts',
    'core/templates/domain/exploration/ExplorationMetadataObjectFactory.ts',
    'core/templates/domain/exploration/StatesObjectFactorySpec.ts',
    'core/templates/domain/exploration/editable-exploration-backend-api.service.spec.ts',
    'core/templates/domain/exploration/param-metadata.model.spec.ts',
    'core/templates/domain/exploration/read-only-exploration-backend-api.service.spec.ts',
    'core/templates/domain/question/QuestionObjectFactorySpec.ts',
    'core/templates/domain/question/editable-question-backend-api.service.spec.ts',
    'core/templates/domain/question/pretest-question-backend-api.service.spec.ts',
    'core/templates/domain/question/question-backend-api.service.spec.ts',
    'core/templates/domain/question/question-update.service.spec.ts',
    'core/templates/domain/question/question-update.service.ts',
    'core/templates/domain/skill/skill-update.service.spec.ts',
    'core/templates/domain/skill/skill-update.service.ts',
    'core/templates/domain/state_card/state-card.model.spec.ts',
    'core/templates/domain/statistics/learner-answer-info.model.ts',
    'core/templates/domain/topic/SubtopicPage.model.spec.ts',
    'core/templates/domain/topic/learner-topic-summary.model.spec.ts',
    'core/templates/domain/topic/newly-created-story.model.spec.ts',
    'core/templates/domain/topic/topic-rights.model.spec.ts',
    'core/templates/domain/topic/topic-update.service.spec.ts',
    'core/templates/domain/topic/topic-update.service.ts',
    'core/templates/filters/convert-html-to-unicode.filter.spec.ts',
    'core/templates/filters/convert-unicode-to-html.filter.spec.ts',
    'core/templates/filters/convert-unicode-to-html.filter.ts',
    'core/templates/filters/convert-unicode-with-params-to-html.filter.spec.ts',
    'core/templates/filters/convert-unicode-with-params-to-html.filter.ts',
    'core/templates/filters/format-rte-preview.filter.spec.ts',
    'core/templates/filters/format-rte-preview.filter.ts',
    'core/templates/filters/format-timer.filter.ts',
    'core/templates/filters/format-timer.pipe.ts',
    'core/templates/filters/parameterize-rule-description.filter.spec.ts',
    'core/templates/filters/parameterize-rule-description.filter.ts',
    'core/templates/filters/remove-duplicates-in-array.pipe.spec.ts',
    'core/templates/filters/string-utility-filters/camel-case-to-hyphens.filter.spec.ts',
    'core/templates/filters/string-utility-filters/camel-case-to-hyphens.filter.ts',
    'core/templates/filters/string-utility-filters/capitalize.filter.spec.ts',
    'core/templates/filters/string-utility-filters/capitalize.filter.ts',
    'core/templates/filters/string-utility-filters/convert-to-plain-text.filter.ts',
    'core/templates/filters/string-utility-filters/get-abbreviated-text.filter.spec.ts',
    'core/templates/filters/string-utility-filters/get-abbreviated-text.filter.ts',
    'core/templates/filters/string-utility-filters/get-abbreviated-text.pipe.spec.ts',
    'core/templates/filters/string-utility-filters/normalize-whitespace-punctuation-and-case.filter.ts',
    'core/templates/filters/string-utility-filters/normalize-whitespace.filter.spec.ts',
    'core/templates/filters/string-utility-filters/normalize-whitespace.filter.ts',
    'core/templates/filters/string-utility-filters/replace-inputs-with-ellipses.filter.spec.ts',
    'core/templates/filters/string-utility-filters/replace-inputs-with-ellipses.filter.ts',
    'core/templates/filters/string-utility-filters/replace-inputs-with-ellipses.pipe.spec.ts',
    'core/templates/filters/string-utility-filters/truncate-and-capitalize.filter.spec.ts',
    'core/templates/filters/string-utility-filters/truncate-and-capitalize.filter.ts',
    'core/templates/filters/string-utility-filters/truncate-at-first-ellipsis.filter.spec.ts',
    'core/templates/filters/string-utility-filters/truncate-at-first-ellipsis.filter.ts',
    'core/templates/filters/string-utility-filters/truncate-at-first-ellipsis.pipe.spec.ts',
    'core/templates/filters/string-utility-filters/truncate-at-first-line.filter.spec.ts',
    'core/templates/filters/string-utility-filters/truncate-at-first-line.filter.ts',
    'core/templates/filters/string-utility-filters/truncate.filter.spec.ts',
    'core/templates/filters/string-utility-filters/truncate.filter.ts',
    'core/templates/filters/string-utility-filters/underscores-to-camel-case.filter.spec.ts',
    'core/templates/filters/string-utility-filters/underscores-to-camel-case.filter.ts',
    'core/templates/filters/string-utility-filters/underscores-to-camel-case.pipe.spec.ts',
    'core/templates/filters/string-utility-filters/wrap-text-with-ellipsis.filter.spec.ts',
    'core/templates/filters/string-utility-filters/wrap-text-with-ellipsis.filter.ts',
    'core/templates/filters/summarize-nonnegative-number.filter.spec.ts',
    'core/templates/filters/summarize-nonnegative-number.filter.ts',
    'core/templates/filters/truncate-input-based-on-interaction-answer-type.filter.ts',
    'core/templates/karma.module.ts',
    'core/templates/pages/Base.ts',
    'core/templates/pages/admin-page/admin-page.import.ts',
    'core/templates/pages/admin-page/roles-tab/admin-roles-tab.component.spec.ts',
    'core/templates/pages/admin-page/roles-tab/admin-roles-tab.component.ts',
    'core/templates/pages/blog-admin-page/blog-admin-page.import.ts',
    'core/templates/pages/blog-dashboard-page/blog-dashboard-page.import.ts',
    'core/templates/pages/blog-dashboard-page/blog-dashboard-tile/blog-dashboard-tile.component.ts',
    'core/templates/pages/blog-dashboard-page/blog-post-editor/blog-post-editor.component.spec.ts',
    'core/templates/pages/blog-dashboard-page/blog-post-editor/blog-post-editor.component.ts',
    'core/templates/pages/blog-dashboard-page/modal-templates/blog-card-preview-modal.component.spec.ts',
    'core/templates/pages/blog-dashboard-page/modal-templates/blog-card-preview-modal.component.ts',
    'core/templates/pages/classroom-page/classroom-page.module.ts',
    'core/templates/pages/collection-editor-page/collection-editor-page.import.ts',
    'core/templates/pages/collection-editor-page/editor-tab/collection-editor-tab.component.spec.ts',
    'core/templates/pages/collection-editor-page/editor-tab/collection-editor-tab.component.ts',
    'core/templates/pages/collection-editor-page/editor-tab/collection-node-creator.component.spec.ts',
    'core/templates/pages/collection-editor-page/editor-tab/collection-node-creator.component.ts',
    'core/templates/pages/collection-editor-page/editor-tab/collection-node-editor.component.spec.ts',
    'core/templates/pages/collection-editor-page/editor-tab/collection-node-editor.component.ts',
    'core/templates/pages/collection-editor-page/modals/collection-editor-pre-publish-modal.component.spec.ts',
    'core/templates/pages/collection-editor-page/modals/collection-editor-pre-publish-modal.component.ts',
    'core/templates/pages/collection-editor-page/modals/collection-editor-save-modal.component.ts',
    'core/templates/pages/collection-editor-page/navbar/collection-editor-navbar.component.spec.ts',
    'core/templates/pages/collection-editor-page/navbar/collection-editor-navbar.component.ts',
    'core/templates/pages/collection-editor-page/services/collection-linearizer.service.spec.ts',
    'core/templates/pages/collection-editor-page/services/collection-linearizer.service.ts',
    'core/templates/pages/collection-editor-page/settings-tab/collection-details-editor.component.spec.ts',
    'core/templates/pages/collection-editor-page/settings-tab/collection-details-editor.component.ts',
    'core/templates/pages/collection-editor-page/settings-tab/collection-permissions-card.component.ts',
    'core/templates/pages/collection-player-page/collection-local-nav/collection-local-nav.component.ts',
    'core/templates/pages/collection-player-page/collection-navbar/collection-navbar.component.ts',
    'core/templates/pages/collection-player-page/collection-node-list/collection-node-list.component.ts',
    'core/templates/pages/collection-player-page/collection-player-page.component.spec.ts',
    'core/templates/pages/collection-player-page/collection-player-page.component.ts',
    'core/templates/pages/collection-player-page/collection-player-page.import.ts',
    'core/templates/pages/contributor-dashboard-admin-page/contributor-dashboard-admin-page.component.spec.ts',
    'core/templates/pages/contributor-dashboard-admin-page/contributor-dashboard-admin-page.component.ts',
    'core/templates/pages/contributor-dashboard-admin-page/contributor-dashboard-admin-page.import.ts',
    'core/templates/pages/contributor-dashboard-admin-page/navbar/contributor-dashboard-admin-navbar.component.ts',
    'core/templates/pages/contributor-dashboard-admin-page/services/contributor-dashboard-admin-backend-api.service.spec.ts',
    'core/templates/pages/contributor-dashboard-page/contributions-and-review/contributions-and-review.component.spec.ts',
    'core/templates/pages/contributor-dashboard-page/contributions-and-review/contributions-and-review.component.ts',
    'core/templates/pages/contributor-dashboard-page/contributor-dashboard-page.component.spec.ts',
    'core/templates/pages/contributor-dashboard-page/contributor-dashboard-page.component.ts',
    'core/templates/pages/contributor-dashboard-page/contributor-dashboard-page.constants.ajs.spec.ts',
    'core/templates/pages/contributor-dashboard-page/contributor-dashboard-page.import.ts',
    'core/templates/pages/contributor-dashboard-page/modal-templates/question-suggestion-editor-modal.controller.spec.ts',
    'core/templates/pages/contributor-dashboard-page/modal-templates/question-suggestion-editor-modal.controller.ts',
    'core/templates/pages/contributor-dashboard-page/modal-templates/question-suggestion-review-modal.controller.spec.ts',
    'core/templates/pages/contributor-dashboard-page/modal-templates/question-suggestion-review-modal.controller.ts',
    'core/templates/pages/contributor-dashboard-page/modal-templates/translation-modal.component.spec.ts',
    'core/templates/pages/contributor-dashboard-page/modal-templates/translation-modal.component.ts',
    'core/templates/pages/contributor-dashboard-page/question-opportunities/question-opportunities.component.spec.ts',
    'core/templates/pages/contributor-dashboard-page/question-opportunities/question-opportunities.component.ts',
    'core/templates/pages/contributor-dashboard-page/services/translate-text.service.spec.ts',
    'core/templates/pages/contributor-dashboard-page/services/translate-text.service.ts',
    'core/templates/pages/contributor-dashboard-page/translation-opportunities/translation-opportunities.component.spec.ts',
    'core/templates/pages/creator-dashboard-page/creator-dashboard-page.component.spec.ts',
    'core/templates/pages/creator-dashboard-page/creator-dashboard-page.component.ts',
    'core/templates/pages/creator-dashboard-page/creator-dashboard-page.import.ts',
    'core/templates/pages/donate-page/donate-page.component.spec.ts',
    'core/templates/pages/error-pages/error-page-root.component.ts',
    'core/templates/pages/error-pages/error-page.component.ts',
    'core/templates/pages/exploration-editor-page/changes-in-human-readable-form/changes-in-human-readable-form.component.spec.ts',
    'core/templates/pages/exploration-editor-page/changes-in-human-readable-form/changes-in-human-readable-form.component.ts',
    'core/templates/pages/exploration-editor-page/editor-navigation/editor-navbar-breadcrumb.component.spec.ts',
    'core/templates/pages/exploration-editor-page/editor-navigation/editor-navbar-breadcrumb.component.ts',
    'core/templates/pages/exploration-editor-page/editor-navigation/editor-navigation.component.spec.ts',
    'core/templates/pages/exploration-editor-page/editor-navigation/editor-navigation.component.ts',
    'core/templates/pages/exploration-editor-page/editor-tab/exploration-editor-tab.component.spec.ts',
    'core/templates/pages/exploration-editor-page/editor-tab/exploration-editor-tab.component.ts',
    'core/templates/pages/exploration-editor-page/editor-tab/graph-directives/exploration-graph.component.spec.ts',
    'core/templates/pages/exploration-editor-page/editor-tab/graph-directives/exploration-graph.component.ts',
    'core/templates/pages/exploration-editor-page/editor-tab/graph-directives/state-graph-visualization.directive.spec.ts',
    'core/templates/pages/exploration-editor-page/editor-tab/graph-directives/state-graph-visualization.directive.ts',
    'core/templates/pages/exploration-editor-page/editor-tab/services/responses.service.spec.ts',
    'core/templates/pages/exploration-editor-page/editor-tab/services/responses.service.ts',
    'core/templates/pages/exploration-editor-page/editor-tab/services/solution-verification.service.spec.ts',
    'core/templates/pages/exploration-editor-page/editor-tab/state-name-editor/state-name-editor.component.spec.ts',
    'core/templates/pages/exploration-editor-page/editor-tab/state-name-editor/state-name-editor.component.ts',
    'core/templates/pages/exploration-editor-page/editor-tab/state-param-changes-editor/state-param-changes-editor.component.spec.ts',
    'core/templates/pages/exploration-editor-page/editor-tab/state-param-changes-editor/state-param-changes-editor.component.ts',
    'core/templates/pages/exploration-editor-page/editor-tab/templates/modal-templates/add-answer-group-modal.controller.spec.ts',
    'core/templates/pages/exploration-editor-page/editor-tab/templates/modal-templates/add-answer-group-modal.controller.ts',
    'core/templates/pages/exploration-editor-page/editor-tab/templates/modal-templates/customize-interaction-modal.component.spec.ts',
    'core/templates/pages/exploration-editor-page/editor-tab/templates/modal-templates/customize-interaction-modal.component.ts',
    'core/templates/pages/exploration-editor-page/editor-tab/templates/modal-templates/exploration-graph-modal.controller.spec.ts',
    'core/templates/pages/exploration-editor-page/editor-tab/templates/modal-templates/exploration-graph-modal.controller.ts',
    'core/templates/pages/exploration-editor-page/editor-tab/templates/modal-templates/teach-oppia-modal.controller.spec.ts',
    'core/templates/pages/exploration-editor-page/editor-tab/templates/modal-templates/teach-oppia-modal.controller.ts',
    'core/templates/pages/exploration-editor-page/editor-tab/test-interaction-panel/test-interaction-panel.component.spec.ts',
    'core/templates/pages/exploration-editor-page/editor-tab/test-interaction-panel/test-interaction-panel.component.ts',
    'core/templates/pages/exploration-editor-page/editor-tab/training-panel/training-data-editor-panel-modal.controller.spec.ts',
    'core/templates/pages/exploration-editor-page/editor-tab/training-panel/training-data-editor-panel-modal.controller.ts',
    'core/templates/pages/exploration-editor-page/editor-tab/training-panel/training-data-editor-panel.service.spec.ts',
    'core/templates/pages/exploration-editor-page/editor-tab/training-panel/training-data-editor-panel.service.ts',
    'core/templates/pages/exploration-editor-page/editor-tab/training-panel/training-data.service.spec.ts',
    'core/templates/pages/exploration-editor-page/editor-tab/training-panel/training-data.service.ts',
    'core/templates/pages/exploration-editor-page/editor-tab/training-panel/training-modal.controller.spec.ts',
    'core/templates/pages/exploration-editor-page/editor-tab/training-panel/training-modal.controller.ts',
    'core/templates/pages/exploration-editor-page/editor-tab/training-panel/training-modal.service.spec.ts',
    'core/templates/pages/exploration-editor-page/editor-tab/training-panel/training-modal.service.ts',
    'core/templates/pages/exploration-editor-page/editor-tab/training-panel/training-panel.component.spec.ts',
    'core/templates/pages/exploration-editor-page/editor-tab/training-panel/training-panel.component.ts',
    'core/templates/pages/exploration-editor-page/editor-tab/unresolved-answers-overview/unresolved-answers-overview.component.spec.ts',
    'core/templates/pages/exploration-editor-page/editor-tab/unresolved-answers-overview/unresolved-answers-overview.component.ts',
    'core/templates/pages/exploration-editor-page/exploration-editor-page.component.spec.ts',
    'core/templates/pages/exploration-editor-page/exploration-editor-page.component.ts',
    'core/templates/pages/exploration-editor-page/exploration-editor-page.import.ts',
    'core/templates/pages/exploration-editor-page/exploration-objective-editor/exploration-objective-editor.component.spec.ts',
    'core/templates/pages/exploration-editor-page/exploration-save-and-publish-buttons/exploration-save-and-publish-buttons.component.spec.ts',
    'core/templates/pages/exploration-editor-page/exploration-save-and-publish-buttons/exploration-save-and-publish-buttons.component.ts',
    'core/templates/pages/exploration-editor-page/exploration-title-editor/exploration-title-editor.component.spec.ts',
    'core/templates/pages/exploration-editor-page/exploration-title-editor/exploration-title-editor.component.ts',
    'core/templates/pages/exploration-editor-page/feedback-tab/feedback-tab.component.spec.ts',
    'core/templates/pages/exploration-editor-page/feedback-tab/feedback-tab.component.ts',
    'core/templates/pages/exploration-editor-page/history-tab/history-tab.component.spec.ts',
    'core/templates/pages/exploration-editor-page/history-tab/history-tab.component.ts',
    'core/templates/pages/exploration-editor-page/history-tab/modal-templates/revert-exploration-modal.component.ts',
    'core/templates/pages/exploration-editor-page/history-tab/services/compare-versions.service.spec.ts',
    'core/templates/pages/exploration-editor-page/history-tab/services/compare-versions.service.ts',
    'core/templates/pages/exploration-editor-page/improvements-tab/improvements-tab.component.spec.ts',
    'core/templates/pages/exploration-editor-page/improvements-tab/improvements-tab.component.ts',
    'core/templates/pages/exploration-editor-page/improvements-tab/needs-guiding-responses-task.component.spec.ts',
    'core/templates/pages/exploration-editor-page/improvements-tab/needs-guiding-responses-task.component.ts',
    'core/templates/pages/exploration-editor-page/improvements-tab/services/improvement-modal.service.spec.ts',
    'core/templates/pages/exploration-editor-page/improvements-tab/services/improvement-modal.service.ts',
    'core/templates/pages/exploration-editor-page/modal-templates/exploration-metadata-modal.controller.spec.ts',
    'core/templates/pages/exploration-editor-page/modal-templates/exploration-metadata-modal.controller.ts',
    'core/templates/pages/exploration-editor-page/modal-templates/exploration-save-modal.controller.spec.ts',
    'core/templates/pages/exploration-editor-page/param-changes-editor/param-changes-editor.component.spec.ts',
    'core/templates/pages/exploration-editor-page/param-changes-editor/param-changes-editor.component.ts',
    'core/templates/pages/exploration-editor-page/param-changes-editor/value-generator-editor.directive.spec.ts',
    'core/templates/pages/exploration-editor-page/param-changes-editor/value-generator-editor.directive.ts',
    'core/templates/pages/exploration-editor-page/preview-tab/preview-tab.component.spec.ts',
    'core/templates/pages/exploration-editor-page/preview-tab/preview-tab.component.ts',
    'core/templates/pages/exploration-editor-page/preview-tab/templates/preview-set-parameters-modal.component.ts',
    'core/templates/pages/exploration-editor-page/services/autosave-info-modals.service.spec.ts',
    'core/templates/pages/exploration-editor-page/services/change-list.service.spec.ts',
    'core/templates/pages/exploration-editor-page/services/change-list.service.ts',
    'core/templates/pages/exploration-editor-page/services/exploration-automatic-text-to-speech.service.ts',
    'core/templates/pages/exploration-editor-page/services/exploration-correctness-feedback.service.ts',
    'core/templates/pages/exploration-editor-page/services/exploration-data.service.spec.ts',
    'core/templates/pages/exploration-editor-page/services/exploration-edits-allowed-backend-api.service.spec.ts',
    'core/templates/pages/exploration-editor-page/services/exploration-init-state-name.service.spec.ts',
    'core/templates/pages/exploration-editor-page/services/exploration-init-state-name.service.ts',
    'core/templates/pages/exploration-editor-page/services/exploration-language-code.service.spec.ts',
    'core/templates/pages/exploration-editor-page/services/exploration-language-code.service.ts',
    'core/templates/pages/exploration-editor-page/services/exploration-param-specs.service.ts',
    'core/templates/pages/exploration-editor-page/services/exploration-property.service.spec.ts',
    'core/templates/pages/exploration-editor-page/services/exploration-property.service.ts',
    'core/templates/pages/exploration-editor-page/services/exploration-rights.service.spec.ts',
    'core/templates/pages/exploration-editor-page/services/exploration-rights.service.ts',
    'core/templates/pages/exploration-editor-page/services/exploration-save.service.spec.ts',
    'core/templates/pages/exploration-editor-page/services/exploration-save.service.ts',
    'core/templates/pages/exploration-editor-page/services/exploration-states.service.ts',
    'core/templates/pages/exploration-editor-page/services/exploration-tags.service.ts',
    'core/templates/pages/exploration-editor-page/services/exploration-title.service.spec.ts',
    'core/templates/pages/exploration-editor-page/services/exploration-warnings.service.spec.ts',
    'core/templates/pages/exploration-editor-page/services/exploration-warnings.service.ts',
    'core/templates/pages/exploration-editor-page/services/graph-data.service.ts',
    'core/templates/pages/exploration-editor-page/services/parameter-metadata.service.spec.ts',
    'core/templates/pages/exploration-editor-page/services/parameter-metadata.service.ts',
    'core/templates/pages/exploration-editor-page/services/router.service.spec.ts',
    'core/templates/pages/exploration-editor-page/services/router.service.ts',
    'core/templates/pages/exploration-editor-page/services/user-email-preferences.service.ts',
    'core/templates/pages/exploration-editor-page/settings-tab/settings-tab.component.spec.ts',
    'core/templates/pages/exploration-editor-page/settings-tab/settings-tab.component.ts',
    'core/templates/pages/exploration-editor-page/settings-tab/templates/moderator-unpublish-exploration-modal.component.ts',
    'core/templates/pages/exploration-editor-page/settings-tab/templates/preview-summary-tile-modal.component.ts',
    'core/templates/pages/exploration-editor-page/statistics-tab/charts/pie-chart.component.spec.ts',
    'core/templates/pages/exploration-editor-page/statistics-tab/charts/pie-chart.component.ts',
    'core/templates/pages/exploration-editor-page/statistics-tab/statistics-tab.component.spec.ts',
    'core/templates/pages/exploration-editor-page/statistics-tab/statistics-tab.component.ts',
    'core/templates/pages/exploration-editor-page/statistics-tab/templates/state-stats-modal.controller.spec.ts',
    'core/templates/pages/exploration-editor-page/suggestion-modal-for-editor-view/exploration-editor-suggestion-modal.controller.spec.ts',
    'core/templates/pages/exploration-editor-page/suggestion-modal-for-editor-view/suggestion-modal-for-exploration-editor.service.spec.ts',
    'core/templates/pages/exploration-editor-page/suggestion-modal-for-editor-view/suggestion-modal-for-exploration-editor.service.ts',
    'core/templates/pages/exploration-editor-page/translation-tab/audio-translation-bar/audio-translation-bar.directive.spec.ts',
    'core/templates/pages/exploration-editor-page/translation-tab/audio-translation-bar/audio-translation-bar.directive.ts',
    'core/templates/pages/exploration-editor-page/translation-tab/modal-templates/add-audio-translation-modal.controller.spec.ts',
    'core/templates/pages/exploration-editor-page/translation-tab/modal-templates/add-audio-translation-modal.controller.ts',
    'core/templates/pages/exploration-editor-page/translation-tab/modal-templates/translation-tab-busy-modal.component.ts',
    'core/templates/pages/exploration-editor-page/translation-tab/modal-templates/welcome-translation-modal.component.ts',
    'core/templates/pages/exploration-editor-page/translation-tab/services/translation-status.service.spec.ts',
    'core/templates/pages/exploration-editor-page/translation-tab/services/translation-status.service.ts',
    'core/templates/pages/exploration-editor-page/translation-tab/services/translation-topic.service.spec.ts',
    'core/templates/pages/exploration-editor-page/translation-tab/services/voiceover-recording.service.ts',
    'core/templates/pages/exploration-editor-page/translation-tab/state-translation-editor/state-translation-editor.component.spec.ts',
    'core/templates/pages/exploration-editor-page/translation-tab/state-translation-editor/state-translation-editor.component.ts',
    'core/templates/pages/exploration-editor-page/translation-tab/state-translation-status-graph/state-translation-status-graph.component.spec.ts',
    'core/templates/pages/exploration-editor-page/translation-tab/state-translation-status-graph/state-translation-status-graph.component.ts',
    'core/templates/pages/exploration-editor-page/translation-tab/state-translation/state-translation.component.spec.ts',
    'core/templates/pages/exploration-editor-page/translation-tab/state-translation/state-translation.component.ts',
    'core/templates/pages/exploration-editor-page/translation-tab/translation-tab.component.spec.ts',
    'core/templates/pages/exploration-editor-page/translation-tab/translation-tab.component.ts',
    'core/templates/pages/exploration-editor-page/translation-tab/translator-overview/translator-overview.component.spec.ts',
    'core/templates/pages/exploration-editor-page/translation-tab/translator-overview/translator-overview.component.ts',
    'core/templates/pages/exploration-player-page/exploration-player-page.import.ts',
    'core/templates/pages/exploration-player-page/layout-directives/content-language-selector.component.spec.ts',
    'core/templates/pages/exploration-player-page/layout-directives/content-language-selector.component.ts',
    'core/templates/pages/exploration-player-page/layout-directives/exploration-footer.component.spec.ts',
    'core/templates/pages/exploration-player-page/layout-directives/exploration-footer.component.ts',
    'core/templates/pages/exploration-player-page/layout-directives/feedback-popup.component.spec.ts',
    'core/templates/pages/exploration-player-page/layout-directives/feedback-popup.component.ts',
    'core/templates/pages/exploration-player-page/layout-directives/learner-local-nav.component.spec.ts',
    'core/templates/pages/exploration-player-page/layout-directives/learner-local-nav.component.ts',
    'core/templates/pages/exploration-player-page/layout-directives/learner-view-info.component.spec.ts',
    'core/templates/pages/exploration-player-page/layout-directives/learner-view-info.component.ts',
    'core/templates/pages/exploration-player-page/layout-directives/progress-nav.component.spec.ts',
    'core/templates/pages/exploration-player-page/layout-directives/progress-nav.component.ts',
    'core/templates/pages/exploration-player-page/learner-experience/conversation-skin.component.spec.ts',
    'core/templates/pages/exploration-player-page/learner-experience/conversation-skin.component.ts',
    'core/templates/pages/exploration-player-page/learner-experience/learner-answer-info-card.component.ts',
    'core/templates/pages/exploration-player-page/learner-experience/ratings-and-recommendations.component.spec.ts',
    'core/templates/pages/exploration-player-page/learner-experience/ratings-and-recommendations.component.ts',
    'core/templates/pages/exploration-player-page/learner-experience/supplemental-card.component.spec.ts',
    'core/templates/pages/exploration-player-page/learner-experience/supplemental-card.component.ts',
    'core/templates/pages/exploration-player-page/learner-experience/tutor-card.component.spec.ts',
    'core/templates/pages/exploration-player-page/learner-experience/tutor-card.component.ts',
    'core/templates/pages/exploration-player-page/modals/display-hint-modal.component.spec.ts',
    'core/templates/pages/exploration-player-page/modals/display-hint-modal.component.ts',
    'core/templates/pages/exploration-player-page/modals/flag-exploration-modal.component.ts',
    'core/templates/pages/exploration-player-page/modals/refresher-exploration-confirmation-modal.component.ts',
    'core/templates/pages/exploration-player-page/services/answer-classification.service.spec.ts',
    'core/templates/pages/exploration-player-page/services/exploration-engine.service.spec.ts',
    'core/templates/pages/exploration-player-page/services/exploration-engine.service.ts',
    'core/templates/pages/exploration-player-page/services/exploration-player-state.service.spec.ts',
    'core/templates/pages/exploration-player-page/services/exploration-player-state.service.ts',
    'core/templates/pages/exploration-player-page/services/image-preloader.service.spec.ts',
    'core/templates/pages/exploration-player-page/services/image-preloader.service.ts',
    'core/templates/pages/exploration-player-page/services/learner-answer-info.service.spec.ts',
    'core/templates/pages/exploration-player-page/services/learner-answer-info.service.ts',
    'core/templates/pages/exploration-player-page/services/learner-local-nav-backend-api.service.ts',
    'core/templates/pages/exploration-player-page/services/learner-view-rating.service.spec.ts',
    'core/templates/pages/exploration-player-page/services/learner-view-rating.service.ts',
    'core/templates/pages/exploration-player-page/services/question-player-engine.service.spec.ts',
    'core/templates/pages/exploration-player-page/services/question-player-engine.service.ts',
    'core/templates/pages/exploration-player-page/services/state-classifier-mapping.service.spec.ts',
    'core/templates/pages/exploration-player-page/templates/lesson-information-card-modal.component.spec.ts',
    'core/templates/pages/exploration-player-page/templates/lesson-information-card-modal.component.ts',
    'core/templates/pages/landing-pages/topic-landing-page/topic-landing-page.component.spec.ts',
    'core/templates/pages/landing-pages/topic-landing-page/topic-landing-page.component.ts',
    'core/templates/pages/learner-dashboard-page/community-lessons-tab.component.spec.ts',
    'core/templates/pages/learner-dashboard-page/community-lessons-tab.component.ts',
    'core/templates/pages/learner-dashboard-page/goals-tab.component.spec.ts',
    'core/templates/pages/learner-dashboard-page/goals-tab.component.ts',
    'core/templates/pages/learner-dashboard-page/home-tab.component.ts',
    'core/templates/pages/learner-dashboard-page/learner-dashboard-page.component.spec.ts',
    'core/templates/pages/learner-dashboard-page/learner-dashboard-page.component.ts',
    'core/templates/pages/learner-dashboard-page/learner-dashboard-page.import.ts',
    'core/templates/pages/learner-dashboard-page/progress-tab.component.spec.ts',
    'core/templates/pages/learner-dashboard-page/progress-tab.component.ts',
    'core/templates/pages/library-page/library-footer/library-footer.component.ts',
    'core/templates/pages/library-page/search-bar/search-bar.component.spec.ts',
    'core/templates/pages/library-page/search-results/activity-tiles-infinity-grid.component.spec.ts',
    'core/templates/pages/library-page/search-results/activity-tiles-infinity-grid.component.ts',
    'core/templates/pages/library-page/search-results/search-results.component.ts',
    'core/templates/pages/oppia-root/app.module.ts',
    'core/templates/pages/oppia-root/routing/app.routing.module.ts',
    'core/templates/pages/oppia-root/routing/guards/can-access-splash-page.guard.spec.ts',
    'core/templates/pages/oppia-root/routing/guards/can-access-splash-page.guard.ts',
    'core/templates/pages/practice-session-page/practice-session-page.component.spec.ts',
    'core/templates/pages/practice-session-page/practice-session-page.component.ts',
    'core/templates/pages/practice-session-page/practice-session-page.import.ts',
    'core/templates/pages/profile-page/profile-page.component.spec.ts',
    'core/templates/pages/profile-page/profile-page.component.ts',
    'core/templates/pages/release-coordinator-page/beam-jobs-tab/beam-jobs-tab.component.spec.ts',
    'core/templates/pages/release-coordinator-page/beam-jobs-tab/beam-jobs-tab.component.ts',
    'core/templates/pages/release-coordinator-page/components/cancel-beam-job-dialog.component.spec.ts',
    'core/templates/pages/release-coordinator-page/components/cancel-beam-job-dialog.component.ts',
    'core/templates/pages/release-coordinator-page/components/start-new-beam-job-dialog.component.spec.ts',
    'core/templates/pages/release-coordinator-page/components/start-new-beam-job-dialog.component.ts',
    'core/templates/pages/release-coordinator-page/components/view-beam-job-output-dialog.component.spec.ts',
    'core/templates/pages/release-coordinator-page/components/view-beam-job-output-dialog.component.ts',
    'core/templates/pages/release-coordinator-page/navbar/release-coordinator-navbar.component.spec.ts',
    'core/templates/pages/release-coordinator-page/navbar/release-coordinator-navbar.component.ts',
    'core/templates/pages/release-coordinator-page/services/release-coordinator-backend-api.service.spec.ts',
    'core/templates/pages/review-test-page/review-test-page.component.spec.ts',
    'core/templates/pages/review-test-page/review-test-page.component.ts',
    'core/templates/pages/review-test-page/review-test-page.import.ts',
    'core/templates/pages/signup-page/signup-page.component.spec.ts',
    'core/templates/pages/signup-page/signup-page.component.ts',
    'core/templates/pages/skill-editor-page/editor-tab/skill-concept-card-editor/skill-concept-card-editor.component.spec.ts',
    'core/templates/pages/skill-editor-page/editor-tab/skill-concept-card-editor/skill-concept-card-editor.component.ts',
    'core/templates/pages/skill-editor-page/editor-tab/skill-concept-card-editor/worked-example-editor.component.spec.ts',
    'core/templates/pages/skill-editor-page/editor-tab/skill-concept-card-editor/worked-example-editor.component.ts',
    'core/templates/pages/skill-editor-page/editor-tab/skill-description-editor/skill-description-editor.component.spec.ts',
    'core/templates/pages/skill-editor-page/editor-tab/skill-description-editor/skill-description-editor.component.ts',
    'core/templates/pages/skill-editor-page/editor-tab/skill-editor-main-tab.directive.spec.ts',
    'core/templates/pages/skill-editor-page/editor-tab/skill-editor-main-tab.directive.ts',
    'core/templates/pages/skill-editor-page/editor-tab/skill-misconceptions-editor/misconception-editor.component.spec.ts',
    'core/templates/pages/skill-editor-page/editor-tab/skill-misconceptions-editor/misconception-editor.component.ts',
    'core/templates/pages/skill-editor-page/editor-tab/skill-misconceptions-editor/skill-misconceptions-editor.component.spec.ts',
    'core/templates/pages/skill-editor-page/editor-tab/skill-misconceptions-editor/skill-misconceptions-editor.component.ts',
    'core/templates/pages/skill-editor-page/editor-tab/skill-prerequisite-skills-editor/skill-prerequisite-skills-editor.component.spec.ts',
    'core/templates/pages/skill-editor-page/editor-tab/skill-prerequisite-skills-editor/skill-prerequisite-skills-editor.component.ts',
    'core/templates/pages/skill-editor-page/editor-tab/skill-preview-modal.component.ts',
    'core/templates/pages/skill-editor-page/editor-tab/skill-rubrics-editor/skill-rubrics-editor.component.ts',
    'core/templates/pages/skill-editor-page/navbar/skill-editor-navbar.directive.spec.ts',
    'core/templates/pages/skill-editor-page/navbar/skill-editor-navbar.directive.ts',
    'core/templates/pages/skill-editor-page/questions-tab/skill-questions-tab.directive.spec.ts',
    'core/templates/pages/skill-editor-page/questions-tab/skill-questions-tab.directive.ts',
    'core/templates/pages/skill-editor-page/services/question-creation-service.spec.ts',
    'core/templates/pages/skill-editor-page/services/question-creation.service.ts',
    'core/templates/pages/skill-editor-page/services/skill-editor-routing.service.spec.ts',
    'core/templates/pages/skill-editor-page/services/skill-editor-routing.service.ts',
    'core/templates/pages/skill-editor-page/services/skill-editor-staleness-detection.service.ts',
    'core/templates/pages/skill-editor-page/services/skill-editor-state.service.spec.ts',
    'core/templates/pages/skill-editor-page/skill-editor-page.component.spec.ts',
    'core/templates/pages/skill-editor-page/skill-editor-page.component.ts',
    'core/templates/pages/skill-editor-page/skill-editor-page.import.ts',
    'core/templates/pages/skill-editor-page/skill-preview-tab/skill-preview-tab.component.ts',
    'core/templates/pages/skill-editor-page/skill-preview-tab/skill-preview-tab.controller.spec.ts',
    'core/templates/pages/splash-page/splash-page.component.spec.ts',
    'core/templates/pages/splash-page/splash-page.component.ts',
    'core/templates/pages/splash-page/splash-page.module.ts',
    'core/templates/pages/story-editor-page/chapter-editor/chapter-editor-tab.component.spec.ts',
    'core/templates/pages/story-editor-page/chapter-editor/chapter-editor-tab.component.ts',
    'core/templates/pages/story-editor-page/editor-tab/story-editor.directive.spec.ts',
    'core/templates/pages/story-editor-page/editor-tab/story-editor.directive.ts',
    'core/templates/pages/story-editor-page/editor-tab/story-node-editor.directive.spec.ts',
    'core/templates/pages/story-editor-page/editor-tab/story-node-editor.directive.ts',
    'core/templates/pages/story-editor-page/modal-templates/new-chapter-title-modal.controller.spec.ts',
    'core/templates/pages/story-editor-page/modal-templates/new-chapter-title-modal.controller.ts',
    'core/templates/pages/story-editor-page/modal-templates/story-editor-save-modal.component.ts',
    'core/templates/pages/story-editor-page/navbar/story-editor-navbar-breadcrumb.component.spec.ts',
    'core/templates/pages/story-editor-page/navbar/story-editor-navbar-breadcrumb.component.ts',
    'core/templates/pages/story-editor-page/navbar/story-editor-navbar.component.spec.ts',
    'core/templates/pages/story-editor-page/navbar/story-editor-navbar.component.ts',
    'core/templates/pages/story-editor-page/services/story-editor-staleness-detection.service.ts',
    'core/templates/pages/story-editor-page/services/story-editor-state.service.spec.ts',
    'core/templates/pages/story-editor-page/story-editor-page.component.spec.ts',
    'core/templates/pages/story-editor-page/story-editor-page.component.ts',
    'core/templates/pages/story-editor-page/story-editor-page.import.ts',
    'core/templates/pages/story-editor-page/story-preview-tab/story-preview-tab.component.spec.ts',
    'core/templates/pages/story-editor-page/story-preview-tab/story-preview-tab.component.ts',
    'core/templates/pages/story-viewer-page/navbar-breadcrumb/story-viewer-navbar-breadcrumb.component.spec.ts',
    'core/templates/pages/story-viewer-page/navbar-breadcrumb/story-viewer-navbar-breadcrumb.component.ts',
    'core/templates/pages/story-viewer-page/navbar-pre-logo-action/story-viewer-navbar-pre-logo-action.component.ts',
    'core/templates/pages/story-viewer-page/story-viewer-page.component.spec.ts',
    'core/templates/pages/story-viewer-page/story-viewer-page.component.ts',
    'core/templates/pages/subtopic-viewer-page/navbar-breadcrumb/subtopic-viewer-navbar-breadcrumb.component.ts',
    'core/templates/pages/subtopic-viewer-page/navbar-pre-logo-action/subtopic-viewer-navbar-pre-logo-action.component.ts',
    'core/templates/pages/subtopic-viewer-page/subtopic-viewer-page.component.ts',
    'core/templates/pages/subtopic-viewer-page/subtopic-viewer-page.import.ts',
    'core/templates/pages/teach-page/teach-page.component.spec.ts',
    'core/templates/pages/teach-page/teach-page.component.ts',
    'core/templates/pages/topic-editor-page/editor-tab/topic-editor-stories-list.component.spec.ts',
    'core/templates/pages/topic-editor-page/editor-tab/topic-editor-stories-list.component.ts',
    'core/templates/pages/topic-editor-page/editor-tab/topic-editor-tab.directive.spec.ts',
    'core/templates/pages/topic-editor-page/editor-tab/topic-editor-tab.directive.ts',
    'core/templates/pages/topic-editor-page/modal-templates/change-subtopic-assignment-modal.component.ts',
    'core/templates/pages/topic-editor-page/modal-templates/create-new-story-modal.controller.spec.ts',
    'core/templates/pages/topic-editor-page/modal-templates/create-new-subtopic-modal.component.spec.ts',
    'core/templates/pages/topic-editor-page/modal-templates/create-new-subtopic-modal.component.ts',
    'core/templates/pages/topic-editor-page/modal-templates/questions-list-select-skill-and-difficulty-modal.component.spec.ts',
    'core/templates/pages/topic-editor-page/modal-templates/questions-list-select-skill-and-difficulty-modal.component.ts',
    'core/templates/pages/topic-editor-page/modal-templates/questions-opportunities-select-difficulty-modal.component.spec.ts',
    'core/templates/pages/topic-editor-page/modal-templates/questions-opportunities-select-difficulty-modal.component.ts',
    'core/templates/pages/topic-editor-page/modal-templates/topic-editor-save-modal.component.ts',
    'core/templates/pages/topic-editor-page/navbar/topic-editor-navbar-breadcrumb.component.ts',
    'core/templates/pages/topic-editor-page/navbar/topic-editor-navbar.component.spec.ts',
    'core/templates/pages/topic-editor-page/navbar/topic-editor-navbar.component.ts',
    'core/templates/pages/topic-editor-page/preview-tab/topic-preview-tab.component.spec.ts',
    'core/templates/pages/topic-editor-page/preview-tab/topic-preview-tab.component.ts',
    'core/templates/pages/topic-editor-page/questions-tab/topic-questions-tab.component.spec.ts',
    'core/templates/pages/topic-editor-page/questions-tab/topic-questions-tab.component.ts',
    'core/templates/pages/topic-editor-page/rearrange-skills-in-subtopics-modal.controller.spec.ts',
    'core/templates/pages/topic-editor-page/rearrange-skills-in-subtopics-modal.controller.ts',
    'core/templates/pages/topic-editor-page/services/create-new-skill-modal.service.spec.ts',
    'core/templates/pages/topic-editor-page/services/create-new-skill-modal.service.ts',
    'core/templates/pages/topic-editor-page/services/entity-creation.service.spec.ts',
    'core/templates/pages/topic-editor-page/services/entity-creation.service.ts',
    'core/templates/pages/topic-editor-page/services/subtopic-validation.service.ts',
    'core/templates/pages/topic-editor-page/services/topic-editor-routing.service.spec.ts',
    'core/templates/pages/topic-editor-page/services/topic-editor-routing.service.ts',
    'core/templates/pages/topic-editor-page/services/topic-editor-state.service.spec.ts',
    'core/templates/pages/topic-editor-page/services/topic-editor-state.service.ts',
    'core/templates/pages/topic-editor-page/services/topic-editor-staleness-detection.service.ts',
    'core/templates/pages/topic-editor-page/subtopic-editor/subtopic-editor-tab.component.spec.ts',
    'core/templates/pages/topic-editor-page/subtopic-editor/subtopic-editor-tab.component.ts',
    'core/templates/pages/topic-editor-page/subtopic-editor/subtopic-preview-tab.component.spec.ts',
    'core/templates/pages/topic-editor-page/subtopic-editor/subtopic-preview-tab.component.ts',
    'core/templates/pages/topic-editor-page/topic-editor-page.component.spec.ts',
    'core/templates/pages/topic-editor-page/topic-editor-page.component.ts',
    'core/templates/pages/topic-editor-page/topic-editor-page.import.ts',
    'core/templates/pages/topic-viewer-page/navbar-breadcrumb/topic-viewer-navbar-breadcrumb.component.spec.ts',
    'core/templates/pages/topic-viewer-page/stories-list/topic-viewer-stories-list.component.ts',
    'core/templates/pages/topic-viewer-page/subtopics-list/subtopics-list.component.ts',
    'core/templates/pages/topic-viewer-page/topic-viewer-page.component.spec.ts',
    'core/templates/pages/topic-viewer-page/topic-viewer-page.import.ts',
    'core/templates/pages/topics-and-skills-dashboard-page/modals/create-new-skill-modal.component.ts',
    'core/templates/pages/topics-and-skills-dashboard-page/modals/delete-topic-modal.component.ts',
    'core/templates/pages/topics-and-skills-dashboard-page/topics-and-skills-dashboard-page.component.spec.ts',
    'core/templates/pages/topics-and-skills-dashboard-page/topics-and-skills-dashboard-page.component.ts',
    'core/templates/pages/topics-and-skills-dashboard-page/topics-and-skills-dashboard-page.import.ts',
    'core/templates/pages/topics-and-skills-dashboard-page/topics-list/topics-list.component.spec.ts',
    'core/templates/pages/topics-and-skills-dashboard-page/topics-list/topics-list.component.ts',
    'core/templates/services/UpgradedServices.ts',
    'core/templates/services/angular-services.index.ts',
    'core/templates/services/exploration-features.service.spec.ts',
    'core/templates/services/exploration-improvements-task-registry.service.ts',
    'core/templates/services/exploration-improvements.service.spec.ts',
    'core/templates/services/exploration-improvements.service.ts',
    'core/templates/services/nested-directives-recursion-timeout-prevention.service.spec.ts',
    'core/templates/services/nested-directives-recursion-timeout-prevention.service.ts',
    'core/templates/services/oppia-rte-parser.service.spec.ts',
    'core/templates/services/oppia-rte-parser.service.ts',
    'core/templates/services/playthrough-issues.service.ts',
    'core/templates/services/playthrough.service.spec.ts',
    'core/templates/services/promo-bar-backend-api.service.spec.ts',
    'core/templates/services/question-validation.service.spec.ts',
    'core/templates/services/questions-list.service.spec.ts',
    'core/templates/services/rte-helper-modal.controller.spec.ts',
    'core/templates/services/rte-helper-modal.controller.ts',
    'core/templates/services/rte-helper.service.spec.ts',
    'core/templates/services/rte-helper.service.ts',
    'core/templates/services/state-interaction-stats.service.spec.ts',
    'core/templates/services/state-interaction-stats.service.ts',
    'core/templates/services/state-top-answers-stats.service.spec.ts',
    'core/templates/services/state-top-answers-stats.service.ts',
    'core/templates/services/translation-file-hash-loader-backend-api.service.ts',
    'core/templates/tests/unit-test-utils.ajs.ts',
    'core/tests/build_sources/extensions/python-program.tokenizer.spec.ts',
    'core/tests/build_sources/templates/pages/Base.ts',
    'core/tests/karma.conf.ts',
    'core/tests/services_sources/ATestFactory.ts',
    'core/tests/services_sources/BTestService.ts',
    'core/tests/services_sources/CTest.service.ts',
    'core/tests/services_sources/DTest.service.ts',
    'core/tests/services_sources/ETestFactory.ts',
    'core/tests/services_sources/F.directive.ts',
    'extensions/interactions/AlgebraicExpressionInput/directives/oppia-interactive-algebraic-expression-input.component.spec.ts',
    'extensions/interactions/AlgebraicExpressionInput/directives/oppia-interactive-algebraic-expression-input.component.ts',
    'extensions/interactions/CodeRepl/directives/oppia-interactive-code-repl.component.spec.ts',
    'extensions/interactions/CodeRepl/directives/oppia-interactive-code-repl.component.ts',
    'extensions/interactions/Continue/directives/oppia-interactive-continue.component.spec.ts',
    'extensions/interactions/Continue/directives/oppia-interactive-continue.component.ts',
    'extensions/interactions/DragAndDropSortInput/directives/oppia-interactive-drag-and-drop-sort-input.component.spec.ts',
    'extensions/interactions/DragAndDropSortInput/directives/oppia-interactive-drag-and-drop-sort-input.component.ts',
    'extensions/interactions/DragAndDropSortInput/directives/oppia-response-drag-and-drop-sort-input.component.ts',
    'extensions/interactions/DragAndDropSortInput/directives/oppia-short-response-drag-and-drop-sort-input.component.ts',
    'extensions/interactions/EndExploration/directives/oppia-interactive-end-exploration.component.spec.ts',
    'extensions/interactions/EndExploration/directives/oppia-interactive-end-exploration.component.ts',
    'extensions/interactions/FractionInput/directives/oppia-interactive-fraction-input.component.spec.ts',
    'extensions/interactions/FractionInput/directives/oppia-interactive-fraction-input.component.ts',
    'extensions/interactions/GraphInput/directives/graph-viz.component.spec.ts',
    'extensions/interactions/GraphInput/directives/graph-viz.component.ts',
    'extensions/interactions/GraphInput/directives/oppia-interactive-graph-input.component.spec.ts',
    'extensions/interactions/GraphInput/directives/oppia-interactive-graph-input.component.ts',
    'extensions/interactions/GraphInput/directives/oppia-response-graph-input.component.spec.ts',
    'extensions/interactions/GraphInput/directives/oppia-short-response-graph-input.component.spec.ts',
    'extensions/interactions/ImageClickInput/directives/oppia-interactive-image-click-input.component.spec.ts',
    'extensions/interactions/ImageClickInput/directives/oppia-interactive-image-click-input.component.ts',
    'extensions/interactions/ImageClickInput/directives/oppia-response-image-click-input.component.spec.ts',
    'extensions/interactions/InteractiveMap/directives/oppia-interactive-interactive-map.component.spec.ts',
    'extensions/interactions/InteractiveMap/directives/oppia-interactive-interactive-map.component.ts',
    'extensions/interactions/ItemSelectionInput/directives/oppia-interactive-item-selection-input.component.spec.ts',
    'extensions/interactions/ItemSelectionInput/directives/oppia-interactive-item-selection-input.component.ts',
    'extensions/interactions/ItemSelectionInput/directives/oppia-response-item-selection-input.component.spec.ts',
    'extensions/interactions/ItemSelectionInput/directives/oppia-response-item-selection-input.component.ts',
    'extensions/interactions/ItemSelectionInput/directives/oppia-short-response-item-selection-input.component.ts',
    'extensions/interactions/MathEquationInput/directives/oppia-interactive-math-equation-input.component.spec.ts',
    'extensions/interactions/MathEquationInput/directives/oppia-interactive-math-equation-input.component.ts',
    'extensions/interactions/MathEquationInput/directives/oppia-response-math-equation-input.component.ts',
    'extensions/interactions/MathEquationInput/directives/oppia-short-response-math-equation-input.component.ts',
    'extensions/interactions/MultipleChoiceInput/directives/oppia-interactive-multiple-choice-input.component.spec.ts',
    'extensions/interactions/MultipleChoiceInput/directives/oppia-interactive-multiple-choice-input.component.ts',
    'extensions/interactions/MusicNotesInput/directives/music-notes-input.spec.ts',
    'extensions/interactions/MusicNotesInput/directives/oppia-interactive-music-notes-input.component.ts',
    'extensions/interactions/MusicNotesInput/directives/oppia-response-music-notes-input.component.ts',
    'extensions/interactions/MusicNotesInput/directives/oppia-short-response-music-notes-input.component.ts',
    'extensions/interactions/NumberWithUnits/directives/oppia-interactive-number-with-units.component.spec.ts',
    'extensions/interactions/NumberWithUnits/directives/oppia-interactive-number-with-units.component.ts',
    'extensions/interactions/NumberWithUnits/directives/oppia-response-number-with-units.component.ts',
    'extensions/interactions/NumberWithUnits/directives/oppia-short-response-number-with-units.component.ts',
    'extensions/interactions/NumericExpressionInput/directives/oppia-interactive-numeric-expression-input.component.spec.ts',
    'extensions/interactions/NumericExpressionInput/directives/oppia-interactive-numeric-expression-input.component.ts',
    'extensions/interactions/NumericExpressionInput/directives/oppia-response-numeric-expression-input.component.ts',
    'extensions/interactions/NumericExpressionInput/directives/oppia-short-response-numeric-expression-input.component.ts',
    'extensions/interactions/NumericInput/directives/oppia-interactive-numeric-input.component.spec.ts',
    'extensions/interactions/NumericInput/directives/oppia-interactive-numeric-input.component.ts',
    'extensions/interactions/NumericInput/directives/oppia-response-numeric-input.component.ts',
    'extensions/interactions/NumericInput/directives/oppia-short-response-numeric-input.component.ts',
    'extensions/interactions/PencilCodeEditor/directives/oppia-response-pencil-code-editor.component.ts',
    'extensions/interactions/PencilCodeEditor/directives/oppia-short-response-pencil-code-editor.component.ts',
    'extensions/interactions/RatioExpressionInput/directives/oppia-interactive-ratio-expression-input.component.spec.ts',
    'extensions/interactions/RatioExpressionInput/directives/oppia-interactive-ratio-expression-input.component.ts',
    'extensions/interactions/RatioExpressionInput/directives/oppia-response-ratio-expression-input.component.ts',
    'extensions/interactions/RatioExpressionInput/directives/oppia-short-response-ratio-expression-input.component.ts',
    'extensions/interactions/SetInput/directives/oppia-interactive-set-input.component.spec.ts',
    'extensions/interactions/SetInput/directives/oppia-interactive-set-input.component.ts',
    'extensions/interactions/TextInput/directives/oppia-interactive-text-input.component.spec.ts',
    'extensions/interactions/TextInput/directives/oppia-interactive-text-input.component.ts',
    'extensions/interactions/TextInput/directives/oppia-response-text-input.component.spec.ts',
    'extensions/interactions/TextInput/directives/oppia-short-response-text-input.component.spec.ts',
    'extensions/interactions/base-validator.spec.ts',
    'extensions/interactions/rules.spec.ts',
    'extensions/objects/templates/coord-two-dim-editor.component.spec.ts',
    'extensions/objects/templates/graph-property-editor.component.spec.ts',
    'extensions/objects/templates/graph-property-editor.component.ts',
    'extensions/objects/templates/image-editor.component.spec.ts',
    'extensions/objects/templates/image-editor.component.ts',
    'extensions/objects/templates/list-of-sets-of-translatable-html-content-ids-editor.component.ts',
    'extensions/objects/templates/parameter-name-editor.component.ts',
    'extensions/objects/templates/skill-selector-editor.component.spec.ts',
    'extensions/objects/templates/skill-selector-editor.component.ts',
    'extensions/objects/templates/svg-editor.component.spec.ts',
    'extensions/objects/templates/svg-editor.component.ts',
    'extensions/rich_text_components/Image/directives/oppia-noninteractive-image.component.spec.ts',
    'extensions/rich_text_components/Image/directives/oppia-noninteractive-image.component.ts',
    'extensions/rich_text_components/Math/directives/oppia-noninteractive-math.component.ts',
    'extensions/rich_text_components/rte-output-display.component.ts',
    'extensions/value_generators/templates/copier.directive.ts',
    'extensions/value_generators/templates/random-selector.directive.spec.ts',
    'extensions/value_generators/templates/random-selector.directive.ts',
    'extensions/visualizations/oppia-visualization-click-hexbins.directive.spec.ts',
    'extensions/visualizations/oppia-visualization-click-hexbins.directive.ts',
    'extensions/visualizations/oppia-visualization-enumerated-frequency-table.directive.spec.ts',
    'extensions/visualizations/oppia-visualization-enumerated-frequency-table.directive.ts',
    'extensions/visualizations/oppia-visualization-sorted-tiles.directive.spec.ts',
    'extensions/visualizations/oppia-visualization-sorted-tiles.directive.ts',
]
# pylint: enable=line-too-long, single-line-pragma

_PARSER = argparse.ArgumentParser(
    description="""
Run the script from the oppia root folder:
    python -m scripts.typescript_checks
Note that the root folder MUST be named 'oppia'.
""")

_PARSER.add_argument(
    '--strict_checks',
    help='optional; if specified, compiles typescript using strict config.',
    action='store_true')

COMPILED_JS_DIR = os.path.join('local_compiled_js_for_test', '')
TSCONFIG_FILEPATH = 'tsconfig.json'
STRICT_TSCONFIG_FILEPATH = 'tsconfig-strict.json'
TEMP_STRICT_TSCONFIG_FILEPATH = 'temp-tsconfig-strict.json'
PREFIXES = ('core', 'extensions', 'typings')


def validate_compiled_js_dir() -> None:
    """Validates that compiled JS dir matches out dir in tsconfig."""
    with utils.open_file(TSCONFIG_FILEPATH, 'r') as f:
        config_data = json.load(f)
        out_dir = os.path.join(config_data['compilerOptions']['outDir'], '')
    if out_dir != COMPILED_JS_DIR:
        raise Exception(
            'COMPILED_JS_DIR: %s does not match the output directory '
            'in %s: %s' % (COMPILED_JS_DIR, TSCONFIG_FILEPATH, out_dir))


def compile_temp_strict_tsconfig(
    config_path: str, error_messages: List[str]
) -> None:
    """Compiles temporary strict TS config with files those are neither
    strictly typed nor present in TS_STRICT_EXCLUDE_PATHS. If there are any
    errors, we restores the original config.

    Args:
        config_path: str. The config that should be used to run the typescript
            checks.
        error_messages: List[str]. A list of error messages produced by
            compiling the strict typescript config.
    """
    # Generate file names from the error messages.
    errors = [x.strip() for x in error_messages]
    # Remove the empty lines and error explanation lines.
    errors = [x for x in errors if x.startswith(PREFIXES)]
    # Remove error explanation lines.
    errors = [x.split('(', 1)[0] for x in errors]
    # Remove the duplicate occurrences of the file names.
    files_with_errors = sorted(set(errors))

    # List of missing files that are neither strictly typed nor present in
    # TS_STRICT_EXCLUDE_PATHS.
    files_not_type_strict = []
    for filename in files_with_errors:
        if filename not in TS_STRICT_EXCLUDE_PATHS:
            files_not_type_strict.append(filename)

    # Add "typings" folder to get global imports while compiling.
    files_not_type_strict.append('typings')

    # Update "include" field of temp-tsconfig-strict.json with files those
    # are neither strict typed nor present in TS_STRICT_EXCLUDE_PATHS.
    # Example: List "files_not_type_strict".
    with utils.open_file(STRICT_TSCONFIG_FILEPATH, 'r') as f:
        strict_ts_config = yaml.safe_load(f)
        strict_ts_config['include'] = files_not_type_strict

    with utils.open_file(TEMP_STRICT_TSCONFIG_FILEPATH, 'w') as f:
        json.dump(strict_ts_config, f, indent=2, sort_keys=True)
        f.write('\n')

    # Compile temp-tsconfig-strict.json with files those are neither strictly
    # typed nor present in TS_STRICT_EXCLUDE_PATHS. All those files
    # present inside include property.
    os.environ['PATH'] = '%s/bin:' % common.NODE_PATH + os.environ['PATH']
    validate_compiled_js_dir()

    if os.path.exists(COMPILED_JS_DIR):
        shutil.rmtree(COMPILED_JS_DIR)

    cmd = ['./node_modules/typescript/bin/tsc', '--project', config_path]
    process = subprocess.Popen(
        cmd, stdout=subprocess.PIPE, encoding='utf-8')

    # The value of `process.stdout` should not be None since we passed
    # the `stdout=subprocess.PIPE` argument to `Popen`.
    assert process.stdout is not None
    error_messages = list(iter(process.stdout.readline, ''))

    # Remove temporary strict TS config.
    if os.path.exists(TEMP_STRICT_TSCONFIG_FILEPATH):
        os.remove(TEMP_STRICT_TSCONFIG_FILEPATH)

    if error_messages:
        print('\n' + '\n'.join(error_messages))
        print(
            '%s Errors found during compilation.\n' % (
                len([x for x in error_messages if x.startswith(PREFIXES)]))
            )
        sys.exit(1)
    else:
        print('Compilation successful!')


def compile_and_check_typescript(config_path: str) -> None:
    """Compiles typescript files and checks the compilation errors.

    Args:
        config_path: str. The config that should be used to run the typescript
            checks.
    """
    # Set strict TS config include property to ["core", "extensions", "typings"]
    # This make sure to restore include property to its original value after the
    # checks get aborted mid-way.
    with utils.open_file(STRICT_TSCONFIG_FILEPATH, 'r') as f:
        strict_ts_config = yaml.safe_load(f)
        strict_ts_config['include'] = PREFIXES

    with utils.open_file(STRICT_TSCONFIG_FILEPATH, 'w') as f:
        json.dump(strict_ts_config, f, indent=2, sort_keys=True)
        f.write('\n')

    os.environ['PATH'] = '%s/bin:' % common.NODE_PATH + os.environ['PATH']
    validate_compiled_js_dir()

    if os.path.exists(COMPILED_JS_DIR):
        shutil.rmtree(COMPILED_JS_DIR)

    print('Compiling and testing typescript...')
    cmd = ['./node_modules/typescript/bin/tsc', '--project', config_path]
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, encoding='utf-8')

    # The value of `process.stdout` should not be None since we passed
    # the `stdout=subprocess.PIPE` argument to `Popen`.
    assert process.stdout is not None
    error_messages = list(iter(process.stdout.readline, ''))

    if config_path == STRICT_TSCONFIG_FILEPATH:
        compile_temp_strict_tsconfig(
            TEMP_STRICT_TSCONFIG_FILEPATH, error_messages)
    else:
        if error_messages:
            print('Errors found during compilation\n')
            print('\n'.join(error_messages))
            sys.exit(1)
        else:
            print('Compilation successful!')


def main(args: Optional[Sequence[str]] = None) -> None:
    """Run the typescript checks."""
    parsed_args = _PARSER.parse_args(args=args)
    compile_and_check_typescript(
        STRICT_TSCONFIG_FILEPATH
        if parsed_args.strict_checks else
        TSCONFIG_FILEPATH)


# The 'no coverage' pragma is used as this line is un-testable. This is because
# it will only be called when typescript_checks.py is used as a script.
if __name__ == '__main__':  # pragma: no cover
    main()
