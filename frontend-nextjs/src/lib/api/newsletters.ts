import { apiClient } from './client';
import { Newsletter, GenerateNewsletterRequest, UpdateNewsletterRequest } from '@/types/newsletter';

export const newslettersApi = {
  async list(workspaceId: string): Promise<Newsletter[]> {
    const response = await apiClient.get<{newsletters: Newsletter[]; count: number; workspace_id: string}>(`/api/v1/newsletters/workspaces/${workspaceId}`);
    if (response.success && response.data && response.data.newsletters) {
      // Backend returns {newsletters: [...], count, workspace_id, filters}
      // Extract the newsletters array from the wrapper object
      return response.data.newsletters;
    }
    return [];
  },

  async get(id: string): Promise<Newsletter> {
    const response = await apiClient.get<Newsletter>(`/api/v1/newsletters/${id}`);
    if (response.success && response.data) {
      return response.data;
    }
    throw new Error(response.error || 'Failed to get newsletter');
  },

  async generate(data: GenerateNewsletterRequest): Promise<Newsletter> {
    try {
      const response = await apiClient.post<any>('/api/v1/newsletters/generate', data);

      console.log('[Newsletter API] Generate response:', response);

      if (response.success && response.data) {
        // Backend returns {message, newsletter, content_items_count, sources_used}
        return response.data.newsletter || response.data;
      }

      // Log detailed error for debugging
      console.error('[Newsletter API] Generation failed:', {
        error: response.error,
        status: response.status,
        data: response.data
      });

      // Extract error message properly
      const errorMessage = typeof response.error === 'string'
        ? response.error
        : response.error?.message || 'Failed to generate newsletter';

      throw new Error(errorMessage);
    } catch (error: any) {
      console.error('[Newsletter API] Exception during generation:', error);
      throw error;
    }
  },

  async update(id: string, data: UpdateNewsletterRequest): Promise<Newsletter> {
    const response = await apiClient.put<Newsletter>(`/api/v1/newsletters/${id}`, data);
    if (response.success && response.data) {
      return response.data;
    }
    throw new Error(response.error || 'Failed to update newsletter');
  },

  async updateHtml(newsletterId: string, htmlContent: string): Promise<Newsletter> {
    const response = await apiClient.patch<{newsletter: Newsletter; message: string}>(
      `/api/v1/newsletters/${newsletterId}/html`,
      { html_content: htmlContent }
    );

    if (response.success && response.data) {
      return response.data.newsletter || response.data;
    }

    throw new Error(response.error || 'Failed to update newsletter HTML');
  },

  async delete(id: string): Promise<void> {
    const response = await apiClient.delete(`/api/v1/newsletters/${id}`);
    if (!response.success) {
      throw new Error(response.error || 'Failed to delete newsletter');
    }
  },
};
